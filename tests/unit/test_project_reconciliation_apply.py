from __future__ import annotations

import subprocess
from pathlib import Path

from ai_engineering.documentation_ownership import (
    apply_documentation_ownership_initialization,
    plan_documentation_ownership_initialization,
)
from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_inspection import (
    ProjectInspectionRequest,
    inspect_project_state,
)
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
            project_description="AUTO-0008 legacy fixture.",
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
            project_description="AUTO-0008 V2 fixture.",
            author="Example Maintainer",
        )
    )
    _commit_baseline(root)
    return root


def _initialize_ownership(root: Path) -> None:
    snapshot = inspect_project_state(ProjectInspectionRequest(root))
    ownership = plan_documentation_ownership_initialization(snapshot)
    assert ownership.updates
    assert not ownership.manual_review
    apply_documentation_ownership_initialization(ownership)


def test_executor_delegates_exact_ownership_step(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)
    plan = plan_project_reconciliation(root)

    result = apply_project_reconciliation_step(plan, 1)

    assert result.state == "applied"
    assert result.write_attempted is True
    assert result.delegated_subsystem == "AUTO-0003"
    assert result.rollback_status == "not_applicable"
    assert result.reinspect_required is True
    assert result.post_apply_state == "healthy"


def test_executor_delegates_exact_documentation_sync_step(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)
    _initialize_ownership(root)
    (root / "notes.txt").write_text("drift\n", encoding="utf-8")
    plan = plan_project_reconciliation(root)

    result = apply_project_reconciliation_step(plan, 1)

    assert result.state == "applied"
    assert result.write_attempted is True
    assert result.delegated_subsystem == "AUTO-0002"
    assert result.reinspect_required is True
    assert result.post_apply_state == "healthy"
    assert "notes.txt" in (root / "PROJECT_MAP.md").read_text(encoding="utf-8")


def test_executor_delegates_exact_registered_migration(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)
    plan = plan_project_reconciliation(root)

    result = apply_project_reconciliation_step(plan, 1)

    assert result.state == "applied"
    assert result.write_attempted is True
    assert result.delegated_subsystem == "AUTO-0004/AUTO-0005"
    assert result.rollback_status == "succeeded"
    assert result.reinspect_required is True
    assert result.post_apply_state == "ready"
    assert (root / ".ai-engineering.toml").is_file()


def test_executor_rejects_stale_plan_without_writes(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)
    plan = plan_project_reconciliation(root)
    current_status = root / "CURRENT_STATUS.md"
    before = current_status.read_bytes()
    (root / "notes.txt").write_text("changed after plan\n", encoding="utf-8")

    result = apply_project_reconciliation_step(plan, 1)

    assert result.state == "stale_plan"
    assert result.write_attempted is False
    assert result.delegated_subsystem is None
    assert result.issues[0].code == "STALE_PLAN"
    assert current_status.read_bytes() == before


def test_executor_rejects_unknown_sequence_without_writes(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)
    plan = plan_project_reconciliation(root)

    result = apply_project_reconciliation_step(plan, 99)

    assert result.state == "manual_review"
    assert result.write_attempted is False
    assert result.workflow == "none"
    assert result.issues[0].code == "STEP_NOT_FOUND"
