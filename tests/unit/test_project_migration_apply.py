from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_migration import (
    ACTION_CREATE_FILE,
    ACTION_DELETE_MACHINE_FILE,
    ACTION_REPLACE_MACHINE_FILE,
    OWNERSHIP_GENERATED_ABSENT,
    OWNERSHIP_MACHINE,
    PYTHON_ENGINEERING_V1_BASELINE,
    MigrationContract,
    MigrationPathRule,
    MigrationRegistry,
    ProjectMigrationRequest,
    plan_project_migration,
)
from ai_engineering.project_migration_apply import (
    ProjectMigrationManualReviewError,
    ProjectMigrationStalePlanError,
    ProjectMigrationVerificationError,
    ProjectMigrationWriteError,
    apply_project_migration,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.rstrip("\r\n")


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "sample-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=root,
            project_name="Sample Project",
            project_description="Migration apply fixture.",
            author="Example Maintainer",
        )
    )
    _git(root, "init")
    _git(root, "config", "user.name", "Test User")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "baseline")
    return root


def _registry(*rules: MigrationPathRule) -> MigrationRegistry:
    return MigrationRegistry(
        (
            MigrationContract(
                migration_id="v1-to-v2",
                source_baselines=(PYTHON_ENGINEERING_V1_BASELINE,),
                target_baseline="python-engineering-v2",
                profiles=("python-engineering",),
                rules=rules,
            ),
        )
    )


def _plan(root: Path, registry: MigrationRegistry):
    return plan_project_migration(
        ProjectMigrationRequest(root, "v1-to-v2"),
        registry,
    )


def test_apply_replaces_creates_and_deletes_atomically(tmp_path: Path) -> None:
    root = _project(tmp_path)
    replace_path = root / "machine.txt"
    delete_path = root / "obsolete.txt"
    replace_path.write_bytes(b"old\n")
    delete_path.write_bytes(b"obsolete\n")
    registry = _registry(
        MigrationPathRule(
            "generated.txt",
            ACTION_CREATE_FILE,
            OWNERSHIP_GENERATED_ABSENT,
            target_content=b"generated\n",
        ),
        MigrationPathRule(
            "machine.txt",
            ACTION_REPLACE_MACHINE_FILE,
            OWNERSHIP_MACHINE,
            source_content=b"old\n",
            target_content=b"new\n",
        ),
        MigrationPathRule(
            "obsolete.txt",
            ACTION_DELETE_MACHINE_FILE,
            OWNERSHIP_MACHINE,
            source_content=b"obsolete\n",
        ),
    )
    plan = _plan(root, registry)
    head_before = _git(root, "rev-parse", "HEAD")
    branch_before = _git(root, "branch", "--show-current")
    index_before = _git(root, "diff", "--cached", "--binary")
    remotes_before = _git(root, "remote", "-v")

    result = apply_project_migration(plan)

    assert replace_path.read_bytes() == b"new\n"
    assert (root / "generated.txt").read_bytes() == b"generated\n"
    assert not delete_path.exists()
    assert result.changed_paths == ("generated.txt", "machine.txt", "obsolete.txt")
    assert _git(root, "rev-parse", "HEAD") == head_before
    assert _git(root, "branch", "--show-current") == branch_before
    assert _git(root, "diff", "--cached", "--binary") == index_before
    assert _git(root, "remote", "-v") == remotes_before


def test_stale_digest_blocks_all_writes(tmp_path: Path) -> None:
    root = _project(tmp_path)
    first = root / "a.txt"
    second = root / "b.txt"
    first.write_bytes(b"old-a")
    second.write_bytes(b"old-b")
    registry = _registry(
        MigrationPathRule(
            "a.txt",
            ACTION_REPLACE_MACHINE_FILE,
            OWNERSHIP_MACHINE,
            source_content=b"old-a",
            target_content=b"new-a",
        ),
        MigrationPathRule(
            "b.txt",
            ACTION_REPLACE_MACHINE_FILE,
            OWNERSHIP_MACHINE,
            source_content=b"old-b",
            target_content=b"new-b",
        ),
    )
    plan = _plan(root, registry)
    second.write_bytes(b"changed-after-plan")

    with pytest.raises(ProjectMigrationStalePlanError, match="Digest guard mismatch"):
        apply_project_migration(plan)

    assert first.read_bytes() == b"old-a"
    assert second.read_bytes() == b"changed-after-plan"


def test_manual_review_plan_performs_no_writes(tmp_path: Path) -> None:
    root = _project(tmp_path)
    target = root / "machine.txt"
    target.write_bytes(b"local-change")
    registry = _registry(
        MigrationPathRule(
            "machine.txt",
            ACTION_REPLACE_MACHINE_FILE,
            OWNERSHIP_MACHINE,
            source_content=b"expected-source",
            target_content=b"target",
        )
    )
    plan = _plan(root, registry)

    with pytest.raises(ProjectMigrationManualReviewError):
        apply_project_migration(plan)

    assert target.read_bytes() == b"local-change"


def test_mid_apply_failure_rolls_back_prior_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _project(tmp_path)
    first = root / "a.txt"
    second = root / "b.txt"
    first.write_bytes(b"old-a")
    second.write_bytes(b"old-b")
    registry = _registry(
        MigrationPathRule(
            "a.txt",
            ACTION_REPLACE_MACHINE_FILE,
            OWNERSHIP_MACHINE,
            source_content=b"old-a",
            target_content=b"new-a",
        ),
        MigrationPathRule(
            "b.txt",
            ACTION_REPLACE_MACHINE_FILE,
            OWNERSHIP_MACHINE,
            source_content=b"old-b",
            target_content=b"new-b",
        ),
    )
    plan = _plan(root, registry)

    import ai_engineering.project_migration_apply as apply_module

    real_replace = apply_module.os.replace
    calls = 0

    def failing_replace(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected failure")
        real_replace(source, destination)

    monkeypatch.setattr(apply_module.os, "replace", failing_replace)

    with pytest.raises(ProjectMigrationWriteError, match="rollback succeeded"):
        apply_project_migration(plan)

    assert first.read_bytes() == b"old-a"
    assert second.read_bytes() == b"old-b"


def test_verification_failure_rolls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _project(tmp_path)
    target = root / "machine.txt"
    target.write_bytes(b"old")
    registry = _registry(
        MigrationPathRule(
            "machine.txt",
            ACTION_REPLACE_MACHINE_FILE,
            OWNERSHIP_MACHINE,
            source_content=b"old",
            target_content=b"new",
        )
    )
    plan = _plan(root, registry)

    import ai_engineering.project_migration_apply as apply_module

    def fail_verify(*args: object, **kwargs: object) -> None:
        raise ProjectMigrationVerificationError("injected verification failure")

    monkeypatch.setattr(apply_module, "_verify_success", fail_verify)

    with pytest.raises(ProjectMigrationVerificationError):
        apply_project_migration(plan)

    assert target.read_bytes() == b"old"


def test_already_target_plan_is_idempotent_noop(tmp_path: Path) -> None:
    root = _project(tmp_path)
    target = root / "generated.txt"
    target.write_bytes(b"target")
    registry = _registry(
        MigrationPathRule(
            "generated.txt",
            ACTION_CREATE_FILE,
            OWNERSHIP_GENERATED_ABSENT,
            target_content=b"target",
        )
    )
    plan = _plan(root, registry)

    assert plan.operations == ()
    result = apply_project_migration(plan)

    assert result.changed_paths == ()
    assert target.read_bytes() == b"target"
