"""Bounded multi-step reconciliation orchestration for AUTO-0009."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .project_reconciliation import (
    ProjectReconciliationPlan,
    plan_project_reconciliation,
)
from .project_reconciliation_apply import (
    ProjectReconciliationApplyResult,
    apply_project_reconciliation_step,
)

OrchestrationState = Literal[
    "complete",
    "no_change",
    "stopped",
    "failed",
    "limit_reached",
]

DEFAULT_MAX_STEPS = 8
MAX_MAX_STEPS = 100


@dataclass(frozen=True)
class ProjectReconciliationOrchestrationIssue:
    """Stable bounded evidence for an orchestration terminal condition."""

    code: str
    detail: str


@dataclass(frozen=True)
class ProjectReconciliationOrchestrationResult:
    """Immutable result of one bounded AUTO-0009 orchestration run."""

    project_root: Path
    state: OrchestrationState
    successful_steps: int
    attempts: tuple[ProjectReconciliationApplyResult, ...]
    final_plan: ProjectReconciliationPlan
    issues: tuple[ProjectReconciliationOrchestrationIssue, ...]


def _issue(
    code: str,
    detail: str,
) -> tuple[ProjectReconciliationOrchestrationIssue, ...]:
    return (ProjectReconciliationOrchestrationIssue(code=code, detail=detail),)


def _result(
    project_root: Path,
    state: OrchestrationState,
    successful_steps: int,
    attempts: list[ProjectReconciliationApplyResult],
    final_plan: ProjectReconciliationPlan,
    *,
    issues: tuple[ProjectReconciliationOrchestrationIssue, ...] = (),
) -> ProjectReconciliationOrchestrationResult:
    return ProjectReconciliationOrchestrationResult(
        project_root=project_root.resolve(),
        state=state,
        successful_steps=successful_steps,
        attempts=tuple(attempts),
        final_plan=final_plan,
        issues=issues,
    )


def _validate_max_steps(max_steps: int) -> None:
    if max_steps < 1:
        raise ValueError("max_steps must be at least 1")
    if max_steps > MAX_MAX_STEPS:
        raise ValueError(f"max_steps must not exceed {MAX_MAX_STEPS}")


def run_project_reconciliation(
    project_root: Path,
    *,
    max_steps: int = DEFAULT_MAX_STEPS,
) -> ProjectReconciliationOrchestrationResult:
    """Run a bounded sequence of freshly planned AUTO-0008 one-step executions."""

    _validate_max_steps(max_steps)
    root = project_root.resolve()
    attempts: list[ProjectReconciliationApplyResult] = []
    successful_steps = 0

    while True:
        plan = plan_project_reconciliation(root)

        if plan.state == "clean":
            terminal = "complete" if attempts else "no_change"
            return _result(root, terminal, successful_steps, attempts, plan)

        if plan.state == "unsupported":
            return _result(
                root,
                "stopped",
                successful_steps,
                attempts,
                plan,
                issues=_issue(
                    "PLAN_UNSUPPORTED",
                    "fresh reconciliation plan is unsupported",
                ),
            )

        if plan.state == "manual_review":
            return _result(
                root,
                "stopped",
                successful_steps,
                attempts,
                plan,
                issues=_issue(
                    "PLAN_MANUAL_REVIEW",
                    "fresh reconciliation plan requires manual review",
                ),
            )

        if not plan.steps:
            return _result(
                root,
                "stopped",
                successful_steps,
                attempts,
                plan,
                issues=_issue(
                    "READY_PLAN_WITHOUT_STEP",
                    "ready reconciliation plan has no executable step",
                ),
            )

        if successful_steps >= max_steps:
            return _result(
                root,
                "limit_reached",
                successful_steps,
                attempts,
                plan,
                issues=_issue(
                    "PROGRESS_LIMIT_REACHED",
                    "eligible work remains after the configured progress limit",
                ),
            )

        step = plan.steps[0]
        result = apply_project_reconciliation_step(plan, step.sequence)
        attempts.append(result)

        if result.state == "applied":
            successful_steps += 1
            continue

        if result.state == "no_change":
            fresh = plan_project_reconciliation(root)
            if fresh.state == "clean":
                return _result(root, "complete", successful_steps, attempts, fresh)
            return _result(
                root,
                "stopped",
                successful_steps,
                attempts,
                fresh,
                issues=_issue(
                    "NO_PROGRESS",
                    "delegated step made no change while executable work remains",
                ),
            )

        fresh = plan_project_reconciliation(root)
        if result.state == "failed":
            return _result(
                root,
                "failed",
                successful_steps,
                attempts,
                fresh,
                issues=_issue(
                    "DELEGATED_STEP_FAILED",
                    "AUTO-0008 delegated execution failed",
                ),
            )

        return _result(
            root,
            "stopped",
            successful_steps,
            attempts,
            fresh,
            issues=_issue(
                "DELEGATED_STEP_REFUSED",
                f"AUTO-0008 stopped with state {result.state}",
            ),
        )
