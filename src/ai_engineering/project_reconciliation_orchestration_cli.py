"""Public CLI formatting for bounded reconciliation orchestration."""

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
    """Print deterministic machine-readable orchestration evidence."""

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
    print(f"policy_decision_count={len(result.policy_decisions)}")
    for decision in result.policy_decisions:
        effective_max_steps = (
            str(decision.effective_max_steps)
            if decision.effective_max_steps is not None
            else "none"
        )
        print(
            "policy_decision="
            f"{decision.workflow}:{decision.state}:{effective_max_steps}"
        )
        for policy_issue in decision.issues:
            print(
                f"policy_issue={policy_issue.code}:"
                f"{_single_line(policy_issue.detail)}"
            )
    print(f"issue_count={len(result.issues)}")
    for orchestration_issue in result.issues:
        print(
            f"issue={orchestration_issue.code}:"
            f"{_single_line(orchestration_issue.detail)}"
        )
    print(f"final_plan_state={result.final_plan.state}")
    print(f"remaining_step_count={len(result.final_plan.steps)}")


def run_reconciliation_orchestration(
    project_root: Path,
    *,
    max_steps: int = DEFAULT_MAX_STEPS,
    policy_path: Path | None = None,
) -> int:
    """Run bounded reconciliation orchestration and return its public exit code."""

    result = run_project_reconciliation(
        project_root,
        max_steps=max_steps,
        policy_path=policy_path,
    )
    print_reconciliation_run_result(result)
    return 0 if result.state in {"complete", "no_change"} else 1
