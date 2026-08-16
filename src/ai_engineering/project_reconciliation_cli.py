"""Public CLI formatting for AUTO-0007 reconciliation plans."""

from __future__ import annotations

from pathlib import Path

from .project_reconciliation import (
    ProjectReconciliationPlan,
    plan_project_reconciliation,
)


def _single_line(value: str) -> str:
    return " ".join(value.replace("\r", "\n").splitlines()).strip()


def print_reconciliation_plan(plan: ProjectReconciliationPlan) -> None:
    """Print the deterministic AUTO-0007 public CLI representation."""

    print(f"project={plan.project_root}")
    print(f"state={plan.state}")
    print(f"current_overall={plan.health.overall_state}")
    print(f"step_count={len(plan.steps)}")
    for step in plan.steps:
        print(
            f"step={step.sequence}:{step.workflow}:{step.state}:"
            f"{_single_line(step.reason)}"
        )
        if step.migration_id is not None:
            print(f"step_migration={step.sequence}:{step.migration_id}")
        for path in step.affected_paths:
            print(f"step_path={step.sequence}:{path}")
        print(
            f"step_reinspect={step.sequence}:"
            f"{str(step.reinspect_after_step).lower()}"
        )
    print(f"reinspect_required={str(plan.reinspect_required).lower()}")
    print(f"issue_count={len(plan.issues)}")
    for issue in plan.issues:
        path = issue.path or "none"
        workflow = issue.workflow or "none"
        print(
            f"issue={issue.code}:{issue.state}:{path}:{workflow}:"
            f"{_single_line(issue.detail)}"
        )
    print(f"expected_state={plan.expected_state}")


def run_reconciliation_plan(project_root: Path) -> int:
    """Run the read-only reconciliation planner and return its CLI exit code."""

    plan = plan_project_reconciliation(project_root)
    print_reconciliation_plan(plan)
    return 0 if plan.state in {"clean", "ready"} else 1
