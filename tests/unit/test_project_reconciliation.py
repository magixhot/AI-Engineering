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
    NEXT_OWNERSHIP_PLAN,
)
from ai_engineering.project_inspection import (
    ProjectInspectionRequest,
    inspect_project_state,
)
from ai_engineering.project_reconciliation import plan_project_reconciliation
from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)


def _bootstrap_v1(tmp_path: Path) -> Path:
    target = tmp_path / "legacy-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=target,
            project_name="Legacy Project",
            project_description="AUTO-0007 V1 fixture.",
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
            project_description="AUTO-0007 V2 fixture.",
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


def test_healthy_v2_returns_clean_plan(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)
    _initialize_ownership(root)

    plan = plan_project_reconciliation(root)

    assert plan.state == "clean"
    assert plan.steps == ()
    assert plan.issues == ()
    assert plan.expected_state == "healthy"
    assert plan.reinspect_required is False
    assert plan.health.overall_state == "healthy"


def test_v2_ownership_initialization_is_first_safe_step(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)

    plan = plan_project_reconciliation(root)

    assert plan.state == "ready"
    assert len(plan.steps) == 1
    step = plan.steps[0]
    assert step.sequence == 1
    assert step.workflow == NEXT_OWNERSHIP_PLAN
    assert step.state == "ready"
    assert step.migration_id is None
    assert step.affected_paths
    assert step.reinspect_after_step is True
    assert plan.expected_state == "reinspect_required"
    assert plan.reinspect_required is True
    assert step.workflow == plan.health.next_action


def test_v1_migration_is_first_safe_step(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)

    plan = plan_project_reconciliation(root)

    assert plan.state == "ready"
    assert len(plan.steps) == 1
    step = plan.steps[0]
    assert step.sequence == 1
    assert step.workflow == NEXT_MIGRATION_PLAN
    assert step.state == "ready"
    assert step.migration_id == "python-engineering-v1-to-v2"
    assert step.reinspect_after_step is True
    assert plan.expected_state == "reinspect_required"
    assert plan.reinspect_required is True
    assert step.workflow == plan.health.next_action


def test_unsupported_project_returns_no_unsafe_steps(tmp_path: Path) -> None:
    root = tmp_path / "unsupported"
    root.mkdir()
    (root / "pyproject.toml").write_text(
        '[project]\nname = "unsupported"\nversion = "1.0.0"\n',
        encoding="utf-8",
    )

    plan = plan_project_reconciliation(root)

    assert plan.state == "unsupported"
    assert plan.steps == ()
    assert plan.expected_state == "unsupported"
    assert plan.health.overall_state == "unsupported"
    assert plan.issues == plan.health.issues
