from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .project_migration import (
    ACTION_CREATE_FILE,
    ACTION_DELETE_MACHINE_FILE,
    ACTION_REPLACE_MACHINE_FILE,
    ProjectMigrationOperation,
    ProjectMigrationPlan,
    detect_project_identity,
)


class ProjectMigrationApplyError(Exception):
    """Controlled AUTO-0004 apply failure."""


class ProjectMigrationManualReviewError(ProjectMigrationApplyError):
    """The migration plan is not eligible for automatic apply."""


class ProjectMigrationStalePlanError(ProjectMigrationApplyError):
    """The project changed after planning."""


class ProjectMigrationWriteError(ProjectMigrationApplyError):
    """A planned filesystem mutation failed."""


class ProjectMigrationRollbackError(ProjectMigrationApplyError):
    """Rollback could not restore the pre-apply state."""


class ProjectMigrationVerificationError(ProjectMigrationApplyError):
    """Post-apply verification failed."""


@dataclass(frozen=True)
class ProjectMigrationResult:
    """Verified result of one successful guarded migration apply."""

    project_root: Path
    migration_id: str
    target_baseline: str
    changed_paths: tuple[str, ...]


@dataclass(frozen=True)
class _GitSnapshot:
    head: str
    branch: str
    index_diff: bytes
    remotes: bytes


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _run_git(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ProjectMigrationApplyError("Git invariant inspection failed") from exc
    return result.stdout.rstrip(b"\r\n")


def _git_snapshot(root: Path) -> _GitSnapshot:
    return _GitSnapshot(
        head=_run_git(root, "rev-parse", "HEAD").decode("ascii"),
        branch=_run_git(root, "branch", "--show-current").decode("utf-8"),
        index_diff=_run_git(root, "diff", "--cached", "--binary"),
        remotes=_run_git(root, "remote", "-v"),
    )


def _bounded_path(root: Path, relative_path: str, *, must_exist: bool) -> Path:
    path = root / relative_path
    try:
        resolved_parent = path.parent.resolve(strict=True)
    except OSError as exc:
        raise ProjectMigrationStalePlanError(
            f"Parent path unavailable for {relative_path}"
        ) from exc
    if not resolved_parent.is_relative_to(root):
        raise ProjectMigrationStalePlanError(
            f"Migration path escapes project root: {relative_path}"
        )
    if must_exist:
        try:
            resolved = path.resolve(strict=True)
        except OSError as exc:
            raise ProjectMigrationStalePlanError(
                f"Migration path unavailable: {relative_path}"
            ) from exc
        if not resolved.is_relative_to(root) or path.is_symlink() or not path.is_file():
            raise ProjectMigrationStalePlanError(
                f"Migration path has unsupported type: {relative_path}"
            )
    elif path.exists() or path.is_symlink():
        raise ProjectMigrationStalePlanError(
            f"Create target is no longer absent: {relative_path}"
        )
    return path


def _preflight(plan: ProjectMigrationPlan) -> tuple[Path, _GitSnapshot]:
    if plan.manual_review:
        raise ProjectMigrationManualReviewError(
            "Migration plan requires manual review"
        )
    root = plan.project_root.resolve(strict=True)
    identity = detect_project_identity(root)
    if identity.baseline != plan.source_baseline:
        raise ProjectMigrationStalePlanError("Project source baseline changed")

    for operation in plan.operations:
        if operation.action == ACTION_CREATE_FILE:
            _bounded_path(root, operation.path, must_exist=False)
            if operation.original_sha256 is not None:
                raise ProjectMigrationStalePlanError(
                    f"Create operation has unexpected digest: {operation.path}"
                )
            if operation.replacement_content is None:
                raise ProjectMigrationStalePlanError(
                    f"Create operation has no content: {operation.path}"
                )
            continue

        path = _bounded_path(root, operation.path, must_exist=True)
        current = path.read_bytes()
        if operation.original_sha256 is None or _digest(current) != operation.original_sha256:
            raise ProjectMigrationStalePlanError(
                f"Digest guard mismatch: {operation.path}"
            )
        if operation.action == ACTION_REPLACE_MACHINE_FILE:
            if operation.replacement_content is None:
                raise ProjectMigrationStalePlanError(
                    f"Replace operation has no content: {operation.path}"
                )
        elif operation.action == ACTION_DELETE_MACHINE_FILE:
            if operation.replacement_content is not None:
                raise ProjectMigrationStalePlanError(
                    f"Delete operation has replacement content: {operation.path}"
                )
        else:
            raise ProjectMigrationStalePlanError(
                f"Unsupported planned action: {operation.action}"
            )

    return root, _git_snapshot(root)


def _stage_replacements(
    root: Path,
    operations: tuple[ProjectMigrationOperation, ...],
) -> tuple[tempfile.TemporaryDirectory[str], dict[str, Path]]:
    temp_dir = tempfile.TemporaryDirectory(prefix="ai-engineering-migration-")
    staged: dict[str, Path] = {}
    base = Path(temp_dir.name)
    for index, operation in enumerate(operations):
        if operation.replacement_content is None:
            continue
        staged_path = base / f"{index:04d}.replacement"
        staged_path.write_bytes(operation.replacement_content)
        staged[operation.path] = staged_path
    return temp_dir, staged


def _restore(
    root: Path,
    originals: dict[str, bytes | None],
    applied: list[ProjectMigrationOperation],
) -> None:
    failures: list[str] = []
    for operation in reversed(applied):
        path = root / operation.path
        original = originals[operation.path]
        try:
            if original is None:
                if path.exists() or path.is_symlink():
                    path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(original)
        except OSError:
            failures.append(operation.path)

    for relative_path, original in originals.items():
        path = root / relative_path
        try:
            if original is None:
                if path.exists() or path.is_symlink():
                    failures.append(relative_path)
            elif not path.is_file() or path.read_bytes() != original:
                failures.append(relative_path)
        except OSError:
            failures.append(relative_path)
    if failures:
        raise ProjectMigrationRollbackError(
            "Rollback verification failed for: " + ", ".join(sorted(set(failures)))
        )


def _verify_success(
    root: Path,
    plan: ProjectMigrationPlan,
    git_before: _GitSnapshot,
) -> None:
    for operation in plan.operations:
        path = root / operation.path
        if operation.action == ACTION_DELETE_MACHINE_FILE:
            if path.exists() or path.is_symlink():
                raise ProjectMigrationVerificationError(
                    f"Deleted path still exists: {operation.path}"
                )
            continue
        if not path.is_file() or path.is_symlink():
            raise ProjectMigrationVerificationError(
                f"Written path has unsupported type: {operation.path}"
            )
        if path.read_bytes() != operation.replacement_content:
            raise ProjectMigrationVerificationError(
                f"Written content mismatch: {operation.path}"
            )

    if _git_snapshot(root) != git_before:
        raise ProjectMigrationVerificationError("Git invariants changed during apply")


def apply_project_migration(plan: ProjectMigrationPlan) -> ProjectMigrationResult:
    """Apply one previously planned migration as an all-or-nothing transaction."""

    root, git_before = _preflight(plan)
    if not plan.operations:
        return ProjectMigrationResult(
            project_root=root,
            migration_id=plan.migration_id,
            target_baseline=plan.target_baseline,
            changed_paths=(),
        )

    originals: dict[str, bytes | None] = {}
    for operation in plan.operations:
        path = root / operation.path
        originals[operation.path] = (
            None if operation.action == ACTION_CREATE_FILE else path.read_bytes()
        )

    temp_dir, staged = _stage_replacements(root, plan.operations)
    applied: list[ProjectMigrationOperation] = []
    try:
        for operation in plan.operations:
            path = root / operation.path
            if operation.action == ACTION_DELETE_MACHINE_FILE:
                path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                staged_path = staged[operation.path]
                os.replace(staged_path, path)
            applied.append(operation)
    except OSError as exc:
        try:
            _restore(root, originals, applied)
        except ProjectMigrationRollbackError as rollback_exc:
            raise rollback_exc from exc
        raise ProjectMigrationWriteError("Migration write failed; rollback succeeded") from exc
    finally:
        temp_dir.cleanup()

    try:
        _verify_success(root, plan, git_before)
    except ProjectMigrationVerificationError:
        _restore(root, originals, applied)
        raise

    return ProjectMigrationResult(
        project_root=root,
        migration_id=plan.migration_id,
        target_baseline=plan.target_baseline,
        changed_paths=tuple(operation.path for operation in plan.operations),
    )
