"""Public CLI formatting for AUTO-0008 guarded reconciliation apply."""

from __future__ import annotations

from pathlib import Path

from .project_reconciliation import plan_project_reconciliation
from .project_reconciliation_apply import (
    ProjectReconciliationApplyResult,
    apply_project_reconciliation_step,
)


def _single_line(value: str) -> str:
    return " ".join(value.replace("\r", "\n").splitlines()).strip()


def print_reconciliation_apply_result(
    result: ProjectReconciliationApplyResult,
) -> None:
    """Print deterministic machine-readable AUTO-0008 apply evidence."""

    print(f"project={result.project_root}")
    print(f"sequence={result.sequence}")
    print(f"workflow={result.workflow}")
    print(f"state={result.state}")
    print(f"write_attempted={str(result.write_attempted).lower()}")
    print(f"delegated_subsystem={result.delegated_subsystem or 'none'}")
    print(f"issue_count={len(result.issues)}")
    for issue in result.issues:
        print(f"issue={issue.code}:{_single_line(issue.detail)}")
    print(f"rollback_status={result.rollback_status}")
    print(f"reinspect_required={str(result.reinspect_required).lower()}")
    print(f"post_apply_state={result.post_apply_state}")


def run_reconciliation_apply(project_root: Path, sequence: int) -> int:
    """Plan current state, apply one exact step, and return the public exit code."""

    plan = plan_project_reconciliation(project_root)
    result = apply_project_reconciliation_step(plan, sequence)
    print_reconciliation_apply_result(result)
    return 0 if result.state in {"applied", "no_change"} else 1
