"""Read-only AUTO-0011 reconciliation approval verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ai_engineering.project_reconciliation_approval import ReconciliationApproval

ApprovalVerificationState = Literal["approved", "approval_refused"]


@dataclass(frozen=True)
class ReconciliationApprovalContext:
    """Fresh authority-relevant context for one reconciliation candidate."""

    project_id: str
    workflow: str
    candidate_inputs: tuple[tuple[str, str], ...]
    git_head: str
    git_branch: str | None
    policy_fingerprint: str | None


@dataclass(frozen=True)
class ReconciliationApprovalMismatch:
    """Stable evidence for one approval/context mismatch."""

    code: str
    detail: str


@dataclass(frozen=True)
class ReconciliationApprovalVerification:
    """Deterministic result of comparing an approval with fresh context."""

    state: ApprovalVerificationState
    mismatches: tuple[ReconciliationApprovalMismatch, ...]


def _mismatch(code: str, detail: str) -> ReconciliationApprovalMismatch:
    return ReconciliationApprovalMismatch(code=code, detail=detail)


def verify_reconciliation_approval(
    approval: ReconciliationApproval,
    context: ReconciliationApprovalContext,
) -> ReconciliationApprovalVerification:
    """Compare one validated approval to fresh context without performing I/O."""

    mismatches: list[ReconciliationApprovalMismatch] = []
    if approval.scope != "single_candidate":
        mismatches.append(
            _mismatch("APPROVAL_SCOPE_MISMATCH", "approval scope is not single_candidate")
        )
    if approval.project_id != context.project_id:
        mismatches.append(
            _mismatch("APPROVAL_PROJECT_MISMATCH", "project identity changed")
        )
    if approval.workflow != context.workflow:
        mismatches.append(
            _mismatch("APPROVAL_CANDIDATE_MISMATCH", "candidate workflow changed")
        )
    if approval.candidate_inputs != tuple(sorted(context.candidate_inputs)):
        mismatches.append(
            _mismatch("APPROVAL_CANDIDATE_MISMATCH", "candidate inputs changed")
        )
    if approval.git_head != context.git_head:
        mismatches.append(_mismatch("APPROVAL_GIT_MISMATCH", "Git HEAD changed"))
    if approval.git_branch != context.git_branch:
        mismatches.append(_mismatch("APPROVAL_GIT_MISMATCH", "Git branch state changed"))
    if approval.policy_fingerprint != context.policy_fingerprint:
        mismatches.append(
            _mismatch("APPROVAL_POLICY_MISMATCH", "effective policy fingerprint changed")
        )

    ordered = tuple(sorted(mismatches, key=lambda item: (item.code, item.detail)))
    return ReconciliationApprovalVerification(
        state="approval_refused" if ordered else "approved",
        mismatches=ordered,
    )
