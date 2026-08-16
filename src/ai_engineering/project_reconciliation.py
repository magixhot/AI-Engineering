"""Read-only engineering project reconciliation planning for AUTO-0007."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .project_health import (
    NEXT_DOCS_PLAN,
    NEXT_MIGRATION_PLAN,
    NEXT_NONE,
    NEXT_OWNERSHIP_PLAN,
    ProjectHealthIssue,
    ProjectHealthReport,
    audit_project_health,
)
from .project_migration import PYTHON_ENGINEERING_V1_TO_V2_MIGRATION

PlanState = Literal["clean", "ready", "manual_review", "unsupported"]
StepState = Literal["ready", "reinspect_required"]
ExpectedState = Literal[
    "healthy",
    "reinspect_required",
    "manual_review",
    "unsupported",
]


@dataclass(frozen=True)
class ProjectReconciliationStep:
    """One approved workflow that can be planned from current project state."""

    sequence: int
    workflow: str
    state: StepState
    reason: str
    migration_id: str | None = None
    affected_paths: tuple[str, ...] = ()
    reinspect_after_step: bool = True


@dataclass(frozen=True)
class ProjectReconciliationPlan:
    """Immutable AUTO-0007 reconciliation plan."""

    project_root: Path
    health: ProjectHealthReport
    state: PlanState
    steps: tuple[ProjectReconciliationStep, ...]
    issues: tuple[ProjectHealthIssue, ...]
    expected_state: ExpectedState

    @property
    def reinspect_required(self) -> bool:
        return any(step.reinspect_after_step for step in self.steps)


def _paths_for_workflow(
    health: ProjectHealthReport,
    workflow: str,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                issue.path
                for issue in health.issues
                if issue.workflow == workflow and issue.path is not None
            }
        )
    )


def _step_for_action(
    health: ProjectHealthReport,
) -> ProjectReconciliationStep | None:
    workflow = health.next_action
    if workflow == NEXT_MIGRATION_PLAN:
        return ProjectReconciliationStep(
            sequence=1,
            workflow=workflow,
            state="ready",
            reason="registered V1-to-V2 migration is the next approved workflow",
            migration_id=PYTHON_ENGINEERING_V1_TO_V2_MIGRATION,
            affected_paths=_paths_for_workflow(health, workflow),
        )
    if workflow == NEXT_OWNERSHIP_PLAN:
        return ProjectReconciliationStep(
            sequence=1,
            workflow=workflow,
            state="ready",
            reason="documentation ownership initialization is required before sync",
            affected_paths=_paths_for_workflow(health, workflow),
        )
    if workflow == NEXT_DOCS_PLAN:
        return ProjectReconciliationStep(
            sequence=1,
            workflow=workflow,
            state="ready",
            reason="managed documentation drift has an approved sync plan",
            affected_paths=_paths_for_workflow(health, workflow),
        )
    return None


def plan_project_reconciliation(project_root: Path) -> ProjectReconciliationPlan:
    """Return the deterministic read-only reconciliation plan for a project."""

    health = audit_project_health(project_root)
    if health.overall_state == "unsupported":
        return ProjectReconciliationPlan(
            project_root=health.project_root,
            health=health,
            state="unsupported",
            steps=(),
            issues=health.issues,
            expected_state="unsupported",
        )
    if health.overall_state == "manual_review":
        return ProjectReconciliationPlan(
            project_root=health.project_root,
            health=health,
            state="manual_review",
            steps=(),
            issues=health.issues,
            expected_state="manual_review",
        )
    if health.overall_state == "healthy" and health.next_action == NEXT_NONE:
        return ProjectReconciliationPlan(
            project_root=health.project_root,
            health=health,
            state="clean",
            steps=(),
            issues=(),
            expected_state="healthy",
        )

    step = _step_for_action(health)
    if step is None:
        issue = ProjectHealthIssue(
            code="RECONCILIATION_UNPLANNABLE",
            state="manual_review",
            detail="health action cannot be mapped to an approved reconciliation step",
            workflow=health.next_action,
        )
        return ProjectReconciliationPlan(
            project_root=health.project_root,
            health=health,
            state="manual_review",
            steps=(),
            issues=tuple((*health.issues, issue)),
            expected_state="manual_review",
        )

    return ProjectReconciliationPlan(
        project_root=health.project_root,
        health=health,
        state="ready",
        steps=(step,),
        issues=health.issues,
        expected_state="reinspect_required",
    )
