"""Pure AUTO-0012 projection from observed reconciliation evidence to receipts."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .project_reconciliation_approval_verification import (
    ReconciliationApprovalVerification,
)
from .project_reconciliation_orchestration import (
    ProjectReconciliationOrchestrationResult,
)
from .project_reconciliation_receipt import (
    ReceiptApplyAttempt,
    ReceiptApprovalVerification,
    ReceiptPolicyDecision,
    ReconciliationExecutionReceipt,
    build_reconciliation_execution_receipt,
)


@dataclass(frozen=True)
class ObservedApprovalVerification:
    """One already-observed approval verification paired with its workflow."""

    workflow: str
    verification: ReconciliationApprovalVerification


@dataclass(frozen=True)
class ReconciliationReceiptProjectionContext:
    """Read-only invocation context required to project truthful receipt evidence."""

    project_id: str
    requested_max_steps: int
    initial_state: str
    git_head: str
    git_branch: str | None
    policy_fingerprint: str | None = None
    approval_digest: str | None = None
    approval_scope: str | None = None
    approval_verifications: tuple[ObservedApprovalVerification, ...] = ()


def _issue_pairs(items: object) -> tuple[tuple[str, str], ...]:
    return tuple((item.code, item.detail) for item in items)  # type: ignore[attr-defined]


def _policy_decisions(
    result: ProjectReconciliationOrchestrationResult,
) -> tuple[ReceiptPolicyDecision, ...]:
    return tuple(
        ReceiptPolicyDecision(
            workflow=decision.workflow,
            state=decision.state,
            effective_max_steps=decision.effective_max_steps,
            issues=tuple(
                (issue.code, issue.detail)
                for issue in decision.issues
            ),
        )
        for decision in result.policy_decisions
    )


def _approval_verifications(
    context: ReconciliationReceiptProjectionContext,
) -> tuple[ReceiptApprovalVerification, ...]:
    return tuple(
        ReceiptApprovalVerification(
            workflow=item.workflow,
            state=item.verification.state,
            issues=tuple(
                (mismatch.code, mismatch.detail)
                for mismatch in item.verification.mismatches
            ),
        )
        for item in context.approval_verifications
    )


def _attempts(
    result: ProjectReconciliationOrchestrationResult,
) -> tuple[ReceiptApplyAttempt, ...]:
    return tuple(
        ReceiptApplyAttempt(
            sequence=attempt.sequence,
            workflow=attempt.workflow,
            state=attempt.state,
            write_attempted=attempt.write_attempted,
            delegated_subsystem=attempt.delegated_subsystem,
            rollback_status=attempt.rollback_status,
            post_apply_state=attempt.post_apply_state,
            issues=tuple(
                (issue.code, issue.detail)
                for issue in attempt.issues
            ),
        )
        for attempt in result.attempts
    )


def _remaining_work(
    result: ProjectReconciliationOrchestrationResult,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (
            f"step:{step.sequence}:{step.workflow}",
            json.dumps(
                {
                    "affected_paths": list(step.affected_paths),
                    "migration_id": step.migration_id,
                    "reinspect_after_step": step.reinspect_after_step,
                    "state": step.state,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        for step in result.final_plan.steps
    )


def project_reconciliation_execution_receipt(
    result: ProjectReconciliationOrchestrationResult,
    context: ReconciliationReceiptProjectionContext,
) -> ReconciliationExecutionReceipt:
    """Project already-observed run evidence without performing I/O or execution."""

    return build_reconciliation_execution_receipt(
        project_id=context.project_id,
        requested_max_steps=context.requested_max_steps,
        initial_state=context.initial_state,
        git_head=context.git_head,
        git_branch=context.git_branch,
        policy_fingerprint=context.policy_fingerprint,
        approval_digest=context.approval_digest,
        approval_scope=context.approval_scope,
        policy_decisions=_policy_decisions(result),
        approval_verifications=_approval_verifications(context),
        attempts=_attempts(result),
        successful_steps=result.successful_steps,
        terminal_state=result.state,
        terminal_issues=tuple(
            (issue.code, issue.detail)
            for issue in result.issues
        ),
        final_plan_state=result.final_plan.state,
        remaining_work=_remaining_work(result),
    )
