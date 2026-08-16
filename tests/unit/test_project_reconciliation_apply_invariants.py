from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_migration_apply import ProjectMigrationRollbackError
from ai_engineering.project_reconciliation import plan_project_reconciliation
from ai_engineering.project_reconciliation_apply import (
    apply_project_reconciliation_step,
)
from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
        shell=False,
        stdin=subprocess.DEVNULL,
    ).stdout.rstrip("\r\n")


def _commit_baseline(root: Path) -> None:
    _git(root, "config", "user.name", "Test User")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "add", "-A")
    _git(root, "commit", "--allow-empty", "-m", "baseline")


def _bootstrap_v1(tmp_path: Path) -> Path:
    root = tmp_path / "legacy-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=root,
            project_name="Legacy Project",
            project_description="AUTO-0008 invariant fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    _commit_baseline(root)
    return root


def _bootstrap_v2(tmp_path: Path) -> Path:
    root = tmp_path / "v2-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=root,
            project_name="V2 Project",
            project_description="AUTO-0008 invariant fixture.",
            author="Example Maintainer",
        )
    )
    _commit_baseline(root)
    return root


def _project_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def _git_invariants(root: Path) -> dict[str, str]:
    return {
        "head": _git(root, "rev-parse", "HEAD"),
        "branch": _git(root, "branch", "--show-current"),
        "index": _git(root, "diff", "--cached", "--binary"),
        "remotes": _git(root, "remote", "-v"),
        "local_config": _git(root, "config", "--local", "--list"),
    }


def test_unsupported_plan_fails_closed_with_zero_executor_writes(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v1(tmp_path)
    (root / ".ai-engineering.toml").write_text(
        'profile = "python-engineering"\nbaseline = "unapproved"\n',
        encoding="utf-8",
    )
    plan = plan_project_reconciliation(root)
    bytes_before = _project_bytes(root)
    git_before = _git_invariants(root)

    result = apply_project_reconciliation_step(plan, 1)

    assert plan.state == "unsupported"
    assert result.state == "unsupported"
    assert result.write_attempted is False
    assert result.delegated_subsystem is None
    assert result.issues[0].code == "PLAN_UNSUPPORTED"
    assert _project_bytes(root) == bytes_before
    assert _git_invariants(root) == git_before


def test_manual_review_plan_fails_closed_with_zero_executor_writes(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v2(tmp_path)
    (root / "CURRENT_STATUS.md").write_text(
        "<!-- ai-engineering:auto0002:current-status:start -->\n",
        encoding="utf-8",
    )
    plan = plan_project_reconciliation(root)
    bytes_before = _project_bytes(root)
    git_before = _git_invariants(root)

    result = apply_project_reconciliation_step(plan, 1)

    assert plan.state == "manual_review"
    assert result.state == "manual_review"
    assert result.write_attempted is False
    assert result.delegated_subsystem is None
    assert result.issues[0].code == "PLAN_MANUAL_REVIEW"
    assert _project_bytes(root) == bytes_before
    assert _git_invariants(root) == git_before


def test_git_branch_change_after_planning_is_stale_and_preserved(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v2(tmp_path)
    plan = plan_project_reconciliation(root)
    _git(root, "switch", "-c", "changed-after-plan")
    bytes_before = _project_bytes(root)
    git_before = _git_invariants(root)

    first = apply_project_reconciliation_step(plan, 1)
    second = apply_project_reconciliation_step(plan, 1)

    assert first == second
    assert first.state == "stale_plan"
    assert first.write_attempted is False
    assert first.delegated_subsystem is None
    assert first.issues[0].code == "STALE_PLAN"
    assert _project_bytes(root) == bytes_before
    assert _git_invariants(root) == git_before


def test_successful_ownership_apply_preserves_git_invariants(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v2(tmp_path)
    _git(root, "remote", "add", "origin", "https://example.invalid/project.git")
    _git(root, "config", "auto0008.invariant", "preserved")
    plan = plan_project_reconciliation(root)
    git_before = _git_invariants(root)

    result = apply_project_reconciliation_step(plan, 1)

    assert result.state == "applied"
    assert result.delegated_subsystem == "AUTO-0003"
    assert result.reinspect_required is True
    assert result.post_apply_state == "healthy"
    assert _git_invariants(root) == git_before


def test_migration_executes_one_step_then_requires_fresh_reinspection(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v1(tmp_path)
    plan = plan_project_reconciliation(root)

    result = apply_project_reconciliation_step(plan, 1)

    assert result.state == "applied"
    assert result.delegated_subsystem == "AUTO-0004/AUTO-0005"
    assert result.reinspect_required is True
    assert result.post_apply_state == "ready"
    assert (root / ".ai-engineering.toml").is_file()
    fresh = plan_project_reconciliation(root)
    assert fresh.state == "ready"
    assert fresh.steps[0].workflow != plan.steps[0].workflow


def test_controlled_rollback_failure_is_bounded_and_stops_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _bootstrap_v1(tmp_path)
    plan = plan_project_reconciliation(root)
    bytes_before = _project_bytes(root)
    git_before = _git_invariants(root)

    import ai_engineering.project_reconciliation_apply as apply_module

    def fail_migration(_plan: object) -> None:
        raise ProjectMigrationRollbackError("injected rollback failure")

    monkeypatch.setattr(apply_module, "apply_project_migration", fail_migration)

    result = apply_project_reconciliation_step(plan, 1)

    assert result.state == "failed"
    assert result.write_attempted is True
    assert result.delegated_subsystem == "AUTO-0004/AUTO-0005"
    assert result.rollback_status == "failed"
    assert result.reinspect_required is True
    assert result.post_apply_state == "unknown"
    assert result.issues[0].code == "ROLLBACK_FAILED"
    assert _project_bytes(root) == bytes_before
    assert _git_invariants(root) == git_before
