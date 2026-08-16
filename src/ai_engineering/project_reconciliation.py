"""Typed read-only engineering project reconciliation planning for AUTO-0007."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .project_health import (
    NEXT_DOCS_PLAN,
    NEXT_MIGRATION_PLAN,
    NEXT_OWNERSHIP_PLAN,
    ProjectHealthIssue,
    ProjectHealthReport,
    audit_project_health,
)
from .project_migration import PYTHON_ENGINEERING_V1_TO_V2_MIGRATION

PlanState = Literal["clean", "ready", "manual_review", "unsupported"]
StepState = Literal["ready", "reinspect_required"]
ExpectedState = Literal[
    "healthy", "reinspect_required", "manual_review", "unsupported"
]


@dataclass(frozen=True)
class ProjectReconciliationStep:
    """One immutable approved workflow in a reconciliation plan."""

    sequence: int
    workflow: str
    state: StepState
    reason: str
    migration_id: str | None = None
    affected_paths: tuple[str, ...] = ()
    reinspect_after_step: bool = False


@dataclass(frozen=True)
class ProjectReconciliationPlan:
    """Immutable AUTO-0007 read-only project reconciliation plan."""

    project_root: Path
    health: ProjectHealthReport
    state: PlanState
    steps: tuple[ProjectReconciliationStep, ...]
    issues: tuple[ProjectHealthIssue, ...]
    reinspect_required: bool
    expected_state: ExpectedState


_STEP_REASONS = {
    NEXT_MIGRATION_PLAN: (
        "registered python-engineering V1 to V2 migration is the authoritative "
        "next workflow"
    ),
    NEXT_OWNERSHIP_PLAN: (
        "approved documentation ownership initialization is the authoritative "
        "next workflow"
    ),
    NEXT_DOCS_PLAN: (
        "approved documentation synchronization is the authoritative next workflow"
    ),
}


def _blocking_issues(
    report: ProjectHealthReport,
) -> tuple[ProjectHealthIssue, ...]:
    return tuple(
        issue
        for issue in report.issues
        if issue.state in {"manual_review", "unsupported"}
    )


def _affected_paths(
    report: ProjectHealthReport,
    workflow: str,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                issue.path
                for issue in report.issues
                if issue.workflow == workflow and issue.path is not None
            }
        )
    )


def _ready_step(report: ProjectHealthReport) -> ProjectReconciliationStep | None:
    workflow = report.next_action
    reason = _STEP_REASONS.get(workflow)
    if reason is None:
        return None
    migration_id = (
        PYTHON_ENGINEERING_V1_TO_V2_MIGRATION
        if workflow == NEXT_MIGRATION_PLAN
        else None
    )
    return ProjectReconciliationStep(
        sequence=1,
        workflow=workflow,
        state="ready",
        reason=reason,
        migration_id=migration_id,
        affected_paths=_affected_paths(report, workflow),
        reinspect_after_step=True,
    )


def plan_project_reconciliation(project_root: Path) -> ProjectReconciliationPlan:
    """Return the one currently safe reconciliation step without applying it."""

    health = audit_project_health(project_root)

    if health.overall_state == "unsupported":
        return ProjectReconciliationPlan(
            project_root=health.project_root,
            health=health,
            state="unsupported",
            steps=(),
            issues=_blocking_issues(health),
            reinspect_required=False,
            expected_state="unsupported",
        )

    if health.overall_state == "manual_review":
        return ProjectReconciliationPlan(
            project_root=health.project_root,
            health=health,
            state="manual_review",
            steps=(),
            issues=_blocking_issues(health),
            reinspect_required=False,
            expected_state="manual_review",
        )

    if health.overall_state == "healthy":
        return ProjectReconciliationPlan(
            project_root=health.project_root,
            health=health,
            state="clean",
            steps=(),
            issues=(),
            reinspect_required=False,
            expected_state="healthy",
        )

    step = _ready_step(health)
    if step is None:
        issue = ProjectHealthIssue(
            code="RECONCILIATION_NEXT_ACTION_UNSUPPORTED",
            state="manual_review",
            detail=(
                "AUTO-0006 did not identify an approved reconciliation workflow"
            ),
            workflow=health.next_action,
        )
        return ProjectReconciliationPlan(
            project_root=health.project_root,
            health=health,
            state="manual_review",
            steps=(),
            issues=(issue,),
            reinspect_required=False,
            expected_state="manual_review",
        )

    return ProjectReconciliationPlan(
        project_root=health.project_root,
        health=health,
        state="ready",
        steps=(step,),
        issues=(),
        reinspect_required=True,
        expected_state="reinspect_required",
    )
