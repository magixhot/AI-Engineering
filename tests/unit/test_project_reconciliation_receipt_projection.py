from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import cast

from ai_engineering.project_reconciliation import ProjectReconciliationPlan
from ai_engineering.project_reconciliation_apply import (
    ProjectReconciliationApplyIssue,
    ProjectReconciliationApplyResult,
)
from ai_engineering.project_reconciliation_approval_verification import (
    ReconciliationApprovalMismatch,
    ReconciliationApprovalVerification,
)
from ai_engineering.project_reconciliation_orchestration import (
    ProjectReconciliationOrchestrationIssue,
    ProjectReconciliationOrchestrationResult,
)
from ai_engineering.project_reconciliation_policy import (
    ReconciliationPolicyDecision,
    ReconciliationPolicyIssue,
)
from ai_engineering.project_reconciliation_receipt import (
    serialize_reconciliation_execution_receipt,
)
from ai_engineering.project_reconciliation_receipt_projection import (
    ObservedApprovalVerification,
    ReconciliationReceiptProjectionContext,
    project_reconciliation_execution_receipt,
)


def _plan() -> ProjectReconciliationPlan:
    step = SimpleNamespace(
        sequence=1,
        workflow="documentation_sync",
        state="ready",
        migration_id=None,
        affected_paths=("README.md",),
        reinspect_after_step=True,
    )
    return cast(
        ProjectReconciliationPlan,
        SimpleNamespace(state="ready", steps=(step,)),
    )


def _result() -> ProjectReconciliationOrchestrationResult:
    attempt = ProjectReconciliationApplyResult(
        project_root=Path("/ignored/presentation/path"),
        sequence=1,
        workflow="documentation_sync",
        state="applied",
        write_attempted=True,
        delegated_subsystem="AUTO-0002",
        issues=(ProjectReconciliationApplyIssue(code="APPLY_NOTE", detail="done"),),
        rollback_status="not_applicable",
        reinspect_required=True,
        post_apply_state="healthy",
    )
    policy = ReconciliationPolicyDecision(
        source=Path("/ignored/policy/path"),
        state="allowed",
        workflow="documentation_sync",
        effective_max_steps=2,
        issues=(ReconciliationPolicyIssue(code="POLICY_NOTE", detail="allowed"),),
        git_branch="main",
        staged_paths=(),
        unstaged_paths=(),
        untracked_paths=(),
    )
    return ProjectReconciliationOrchestrationResult(
        project_root=Path("/ignored/presentation/path"),
        state="limit_reached",
        successful_steps=1,
        attempts=(attempt,),
        policy_decisions=(policy,),
        final_plan=_plan(),
        issues=(
            ProjectReconciliationOrchestrationIssue(
                code="PROGRESS_LIMIT_REACHED",
                detail="eligible work remains",
            ),
        ),
    )


def _context() -> ReconciliationReceiptProjectionContext:
    verification = ReconciliationApprovalVerification(
        state="approval_refused",
        mismatches=(
            ReconciliationApprovalMismatch(
                code="APPROVAL_GIT_MISMATCH",
                detail="Git HEAD changed",
            ),
        ),
    )
    return ReconciliationReceiptProjectionContext(
        project_id="project-v1:demo",
        requested_max_steps=8,
        initial_state="ready",
        git_head="abc123",
        git_branch="main",
        policy_fingerprint="policy-sha256:demo",
        approval_digest="approval-sha256-demo",
        approval_scope="single_candidate",
        approval_verifications=(
            ObservedApprovalVerification(
                workflow="documentation_sync",
                verification=verification,
            ),
        ),
    )


def test_projection_captures_truthful_ordered_run_evidence() -> None:
    receipt = project_reconciliation_execution_receipt(_result(), _context())

    assert receipt.project_id == "project-v1:demo"
    assert receipt.initial_state == "ready"
    assert receipt.terminal_state == "limit_reached"
    assert receipt.successful_steps == 1
    assert receipt.policy_decisions[0].state == "allowed"
    assert receipt.approval_verifications[0].state == "approval_refused"
    assert receipt.attempts[0].write_attempted is True
    assert receipt.attempts[0].state == "applied"
    assert receipt.final_plan_state == "ready"
    assert receipt.remaining_work[0][0] == "step:1:documentation_sync"


def test_projection_is_deterministic_and_does_not_use_local_paths() -> None:
    result = _result()
    context = _context()

    first = project_reconciliation_execution_receipt(result, context)
    second = project_reconciliation_execution_receipt(result, context)
    raw = serialize_reconciliation_execution_receipt(first)

    assert first == second
    assert first.digest == second.digest
    assert b"/ignored/presentation/path" not in raw
    assert b"/ignored/policy/path" not in raw


def test_projection_does_not_mutate_result_or_context() -> None:
    result = _result()
    context = _context()
    before_result = repr(result)
    before_context = repr(context)

    project_reconciliation_execution_receipt(result, context)

    assert repr(result) == before_result
    assert repr(context) == before_context


def test_projection_records_refusal_without_inventing_write() -> None:
    result = ProjectReconciliationOrchestrationResult(
        project_root=Path("/ignored"),
        state="approval_refused",
        successful_steps=0,
        attempts=(),
        policy_decisions=(),
        final_plan=_plan(),
        issues=(
            ProjectReconciliationOrchestrationIssue(
                code="APPROVAL_GIT_MISMATCH",
                detail="Git HEAD changed",
            ),
        ),
    )

    receipt = project_reconciliation_execution_receipt(result, _context())

    assert receipt.terminal_state == "approval_refused"
    assert receipt.successful_steps == 0
    assert receipt.attempts == ()
    assert receipt.terminal_issues == (("APPROVAL_GIT_MISMATCH", "Git HEAD changed"),)


def test_projection_has_no_execution_or_filesystem_side_effects(tmp_path: Path) -> None:
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("unchanged", encoding="utf-8")
    before = tuple(sorted(path.name for path in tmp_path.iterdir()))

    project_reconciliation_execution_receipt(_result(), _context())

    after = tuple(sorted(path.name for path in tmp_path.iterdir()))
    assert before == after
    assert sentinel.read_text(encoding="utf-8") == "unchanged"
