"""Public CLI formatting for AUTO-0009 bounded reconciliation orchestration."""

from __future__ import annotations

from pathlib import Path

from .project_reconciliation_orchestration import (
    DEFAULT_MAX_STEPS,
    ProjectReconciliationOrchestrationResult,
    run_project_reconciliation,
)


def _single_line(value: str) -> str:
    return " ".join(value.replace("\r", "\n").splitlines()).strip()


def print_reconciliation_run_result(
    result: ProjectReconciliationOrchestrationResult,
) -> None:
    """Print deterministic machine-readable AUTO-0009 orchestration evidence."""

    print(f"project={result.project_root}")
    print(f"state={result.state}")
    print(f"successful_steps={result.successful_steps}")
    print(f"attempt_count={len(result.attempts)}")
    for attempt in result.attempts:
        print(
            "attempt="
            f"{attempt.sequence}:{attempt.workflow}:{attempt.state}:"
            f"{str(attempt.write_attempted).lower()}"
        )
    print(f"issue_count={len(result.issues)}")
    for issue in result.issues:
        print(f"issue={issue.code}:{_single_line(issue.detail)}")
    print(f"final_plan_state={result.final_plan.state}")
    print(f"remaining_step_count={len(result.final_plan.steps)}")


def run_reconciliation_orchestration(
    project_root: Path,
    *,
    max_steps: int = DEFAULT_MAX_STEPS,
) -> int:
    """Run bounded reconciliation orchestration and return its public exit code."""

    result = run_project_reconciliation(project_root, max_steps=max_steps)
    print_reconciliation_run_result(result)
    return 0 if result.state in {"complete", "no_change"} else 1
