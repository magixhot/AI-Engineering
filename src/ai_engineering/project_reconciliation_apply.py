"""Guarded one-step project reconciliation execution for AUTO-0008."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .documentation_apply import apply_documentation_sync
from .documentation_ownership import (
    DocumentationOwnershipError,
    apply_documentation_ownership_initialization,
    plan_documentation_ownership_initialization,
)
from .documentation_sync import (
    DocumentationSyncError,
    detect_documentation_drift,
    plan_documentation_sync,
)
from .project_health import NEXT_DOCS_PLAN, NEXT_MIGRATION_PLAN, NEXT_OWNERSHIP_PLAN
from .project_inspection import ProjectInspectionRequest, inspect_project_state
from .project_migration import (
    DEFAULT_MIGRATION_REGISTRY,
    ProjectMigrationError,
    ProjectMigrationRequest,
    plan_project_migration,
)
from .project_migration_apply import (
    ProjectMigrationApplyError,
    ProjectMigrationManualReviewError,
    ProjectMigrationRollbackError,
    ProjectMigrationStalePlanError,
    apply_project_migration,
)
from .project_reconciliation import (
    ProjectReconciliationPlan,
    ProjectReconciliationStep,
    plan_project_reconciliation,
)

ApplyState = Literal[
    "applied",
    "no_change",
    "stale_plan",
    "manual_review",
    "unsupported",
    "failed",
]
RollbackStatus = Literal[
    "not_applicable",
    "not_attempted",
    "succeeded",
    "failed",
    "unknown",
]
PostApplyState = Literal[
    "healthy",
    "ready",
    "manual_review",
    "unsupported",
    "unknown",
]


@dataclass(frozen=True)
class ProjectReconciliationApplyIssue:
    """Stable bounded evidence for one guarded apply result."""

    code: str
    detail: str


@dataclass(frozen=True)
class ProjectReconciliationApplyResult:
    """Immutable result of one AUTO-0008 guarded execution attempt."""

    project_root: Path
    sequence: int
    workflow: str
    state: ApplyState
    write_attempted: bool
    delegated_subsystem: str | None
    issues: tuple[ProjectReconciliationApplyIssue, ...]
    rollback_status: RollbackStatus
    reinspect_required: bool
    post_apply_state: PostApplyState


_DELEGATED_SUBSYSTEMS = {
    NEXT_DOCS_PLAN: "AUTO-0002",
    NEXT_OWNERSHIP_PLAN: "AUTO-0003",
    NEXT_MIGRATION_PLAN: "AUTO-0004/AUTO-0005",
}


def _issue(code: str, detail: str) -> tuple[ProjectReconciliationApplyIssue, ...]:
    return (ProjectReconciliationApplyIssue(code=code, detail=detail),)


def _result(
    plan: ProjectReconciliationPlan,
    sequence: int,
    workflow: str,
    state: ApplyState,
    *,
    write_attempted: bool = False,
    delegated_subsystem: str | None = None,
    issues: tuple[ProjectReconciliationApplyIssue, ...] = (),
    rollback_status: RollbackStatus = "not_applicable",
    reinspect_required: bool = False,
    post_apply_state: PostApplyState = "unknown",
) -> ProjectReconciliationApplyResult:
    return ProjectReconciliationApplyResult(
        project_root=plan.project_root.resolve(),
        sequence=sequence,
        workflow=workflow,
        state=state,
        write_attempted=write_attempted,
        delegated_subsystem=delegated_subsystem,
        issues=issues,
        rollback_status=rollback_status,
        reinspect_required=reinspect_required,
        post_apply_state=post_apply_state,
    )


def _selected_step(
    plan: ProjectReconciliationPlan,
    sequence: int,
) -> ProjectReconciliationStep | None:
    return next((step for step in plan.steps if step.sequence == sequence), None)


def _post_apply_state(plan: ProjectReconciliationPlan) -> PostApplyState:
    if plan.state == "clean":
        return "healthy"
    if plan.state == "ready":
        return "ready"
    if plan.state == "manual_review":
        return "manual_review"
    return "unsupported"


def _prewrite_gate(
    plan: ProjectReconciliationPlan,
    sequence: int,
) -> tuple[ProjectReconciliationStep | None, ProjectReconciliationApplyResult | None]:
    selected = _selected_step(plan, sequence)
    workflow = selected.workflow if selected is not None else "none"

    if plan.state == "unsupported":
        return None, _result(
            plan,
            sequence,
            workflow,
            "unsupported",
            issues=_issue("PLAN_UNSUPPORTED", "reconciliation plan is unsupported"),
        )
    if plan.state == "manual_review":
        return None, _result(
            plan,
            sequence,
            workflow,
            "manual_review",
            issues=_issue(
                "PLAN_MANUAL_REVIEW",
                "reconciliation plan requires manual review",
            ),
        )
    if selected is None:
        return None, _result(
            plan,
            sequence,
            workflow,
            "manual_review",
            issues=_issue(
                "STEP_NOT_FOUND",
                "selected reconciliation step does not exist",
            ),
        )
    if selected.state != "ready":
        return None, _result(
            plan,
            sequence,
            selected.workflow,
            "manual_review",
            issues=_issue(
                "STEP_NOT_EXECUTABLE",
                "selected step is a reinspection boundary",
            ),
        )
    if selected.workflow not in _DELEGATED_SUBSYSTEMS:
        return None, _result(
            plan,
            sequence,
            selected.workflow,
            "manual_review",
            issues=_issue(
                "WORKFLOW_NOT_ALLOWED",
                "selected workflow has no approved executor mapping",
            ),
        )

    fresh = plan_project_reconciliation(plan.project_root)
    if fresh.state == "unsupported":
        return None, _result(
            plan,
            sequence,
            selected.workflow,
            "unsupported",
            issues=_issue(
                "CURRENT_STATE_UNSUPPORTED",
                "current project state is unsupported",
            ),
        )
    if fresh.state == "manual_review":
        return None, _result(
            plan,
            sequence,
            selected.workflow,
            "manual_review",
            issues=_issue(
                "CURRENT_STATE_MANUAL_REVIEW",
                "current project state requires manual review",
            ),
        )
    if fresh.state == "clean":
        return None, _result(
            plan,
            sequence,
            selected.workflow,
            "no_change",
            post_apply_state="healthy",
        )
    if fresh != plan:
        return None, _result(
            plan,
            sequence,
            selected.workflow,
            "stale_plan",
            issues=_issue(
                "STALE_PLAN",
                "project or Git state changed after reconciliation planning",
            ),
        )

    return selected, None


def _apply_ownership(plan: ProjectReconciliationPlan) -> tuple[bool, RollbackStatus]:
    snapshot = inspect_project_state(ProjectInspectionRequest(plan.project_root))
    ownership_plan = plan_documentation_ownership_initialization(snapshot)
    if ownership_plan.manual_review:
        raise DocumentationOwnershipError(
            "ownership initialization now requires manual review"
        )
    if not ownership_plan.updates:
        return False, "not_applicable"
    apply_documentation_ownership_initialization(ownership_plan)
    return True, "not_applicable"


def _apply_docs(plan: ProjectReconciliationPlan) -> tuple[bool, RollbackStatus]:
    snapshot = inspect_project_state(ProjectInspectionRequest(plan.project_root))
    drift = detect_documentation_drift(snapshot)
    sync_plan = plan_documentation_sync(drift)
    if not sync_plan.updates:
        return False, "not_applicable"
    apply_documentation_sync(sync_plan)
    return True, "not_applicable"


def _apply_migration(
    plan: ProjectReconciliationPlan,
    step: ProjectReconciliationStep,
) -> tuple[bool, RollbackStatus]:
    if step.migration_id is None:
        raise ProjectMigrationError("planned migration step has no migration id")
    migration_plan = plan_project_migration(
        ProjectMigrationRequest(plan.project_root, step.migration_id),
        DEFAULT_MIGRATION_REGISTRY,
    )
    if migration_plan.manual_review:
        raise ProjectMigrationManualReviewError("migration now requires manual review")
    if not migration_plan.operations:
        return False, "not_applicable"
    apply_project_migration(migration_plan)
    return True, "succeeded"


def apply_project_reconciliation_step(
    plan: ProjectReconciliationPlan,
    sequence: int,
) -> ProjectReconciliationApplyResult:
    """Apply at most one exact eligible AUTO-0007 step through its owning subsystem."""

    selected, refusal = _prewrite_gate(plan, sequence)
    if refusal is not None:
        return refusal
    if selected is None:
        raise AssertionError("prewrite gate returned neither selected step nor refusal")

    subsystem = _DELEGATED_SUBSYSTEMS[selected.workflow]
    try:
        if selected.workflow == NEXT_OWNERSHIP_PLAN:
            changed, rollback_status = _apply_ownership(plan)
        elif selected.workflow == NEXT_DOCS_PLAN:
            changed, rollback_status = _apply_docs(plan)
        elif selected.workflow == NEXT_MIGRATION_PLAN:
            changed, rollback_status = _apply_migration(plan, selected)
        else:  # pragma: no cover - allow-list gate makes this unreachable
            raise AssertionError("unreachable workflow mapping")
    except ProjectMigrationStalePlanError as exc:
        return _result(
            plan,
            sequence,
            selected.workflow,
            "stale_plan",
            delegated_subsystem=subsystem,
            issues=_issue("DELEGATE_STALE_PLAN", str(exc)),
        )
    except ProjectMigrationManualReviewError as exc:
        return _result(
            plan,
            sequence,
            selected.workflow,
            "manual_review",
            delegated_subsystem=subsystem,
            issues=_issue("DELEGATE_MANUAL_REVIEW", str(exc)),
        )
    except ProjectMigrationRollbackError as exc:
        return _result(
            plan,
            sequence,
            selected.workflow,
            "failed",
            write_attempted=True,
            delegated_subsystem=subsystem,
            issues=_issue("ROLLBACK_FAILED", str(exc)),
            rollback_status="failed",
            reinspect_required=True,
        )
    except (
        ProjectMigrationApplyError,
        DocumentationOwnershipError,
        DocumentationSyncError,
    ) as exc:
        return _result(
            plan,
            sequence,
            selected.workflow,
            "failed",
            write_attempted=True,
            delegated_subsystem=subsystem,
            issues=_issue("DELEGATED_APPLY_FAILED", str(exc)),
            rollback_status="unknown",
            reinspect_required=True,
        )

    fresh = plan_project_reconciliation(plan.project_root)
    if not changed:
        return _result(
            plan,
            sequence,
            selected.workflow,
            "no_change",
            delegated_subsystem=subsystem,
            rollback_status=rollback_status,
            reinspect_required=selected.reinspect_after_step,
            post_apply_state=_post_apply_state(fresh),
        )
    return _result(
        plan,
        sequence,
        selected.workflow,
        "applied",
        write_attempted=True,
        delegated_subsystem=subsystem,
        rollback_status=rollback_status,
        reinspect_required=selected.reinspect_after_step,
        post_apply_state=_post_apply_state(fresh),
    )
