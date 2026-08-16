from __future__ import annotations

from pathlib import Path

from ai_engineering.documentation_ownership import (
    apply_documentation_ownership_initialization,
    plan_documentation_ownership_initialization,
)
from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_health import (
    NEXT_MIGRATION_PLAN,
    NEXT_NONE,
    NEXT_OWNERSHIP_PLAN,
    audit_project_health,
)
from ai_engineering.project_inspection import (
    ProjectInspectionRequest,
    inspect_project_state,
)
from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)
from ai_engineering.python_engineering_baseline import PYTHON_ENGINEERING_V2_BASELINE


def _bootstrap_v1(tmp_path: Path) -> Path:
    target = tmp_path / "legacy-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=target,
            project_name="Legacy Project",
            project_description="AUTO-0006 legacy fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    return target


def _bootstrap_v2(tmp_path: Path) -> Path:
    target = tmp_path / "v2-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=target,
            project_name="V2 Project",
            project_description="AUTO-0006 V2 fixture.",
            author="Example Maintainer",
        )
    )
    return target


def _initialize_ownership(root: Path) -> None:
    snapshot = inspect_project_state(ProjectInspectionRequest(root))
    plan = plan_documentation_ownership_initialization(snapshot)
    assert not plan.manual_review
    assert plan.updates
    apply_documentation_ownership_initialization(plan)


def test_v1_reports_registered_migration_as_highest_priority_action(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v1(tmp_path)

    report = audit_project_health(root)

    assert report.overall_state == "action_required"
    assert report.identity is not None
    assert report.identity.baseline == "python-engineering-v1"
    assert report.migration_state == "ready"
    assert report.documentation_ownership_state == "initialization_available"
    assert report.documentation_sync_state == "blocked"
    assert report.next_action == NEXT_MIGRATION_PLAN
    assert any(issue.code == "MIGRATION_AVAILABLE" for issue in report.issues)


def test_v2_without_markers_recommends_ownership_initialization(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)

    report = audit_project_health(root)

    assert report.overall_state == "action_required"
    assert report.identity is not None
    assert report.identity.baseline == PYTHON_ENGINEERING_V2_BASELINE
    assert report.migration_state == "already_target"
    assert report.documentation_ownership_state == "initialization_available"
    assert report.documentation_sync_state == "blocked"
    assert report.next_action == NEXT_OWNERSHIP_PLAN


def test_v2_with_initialized_synchronized_docs_is_healthy(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)
    _initialize_ownership(root)

    report = audit_project_health(root)

    assert report.overall_state == "healthy"
    assert report.documentation_ownership_state == "initialized"
    assert report.documentation_sync_state == "clean"
    assert report.migration_state == "already_target"
    assert report.next_action == NEXT_NONE
    assert report.issues == ()


def test_unsupported_project_fails_closed_without_heuristic_identity(
    tmp_path: Path,
) -> None:
    root = tmp_path / "arbitrary"
    root.mkdir()
    (root / "pyproject.toml").write_text(
        '[project]\nname = "arbitrary"\nversion = "1.0.0"\n',
        encoding="utf-8",
    )

    report = audit_project_health(root)

    assert report.overall_state == "unsupported"
    assert report.identity is None
    assert report.next_action == "manual_review"
    assert tuple(issue.code for issue in report.issues) == ("IDENTITY_UNSUPPORTED",)


def test_health_audit_is_deterministic_and_read_only(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)
    observed = tuple(
        path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts
    )
    before = {path.relative_to(root).as_posix(): path.read_bytes() for path in observed}

    first = audit_project_health(root)
    second = audit_project_health(root)

    after = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert first == second
    assert after == before
    assert tuple(issue.code for issue in first.issues) == tuple(
        sorted(issue.code for issue in first.issues)
    )
