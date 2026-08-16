from dataclasses import replace

from ai_engineering.project_reconciliation_approval import build_reconciliation_approval
from ai_engineering.project_reconciliation_approval_verification import (
    ReconciliationApprovalContext,
    verify_reconciliation_approval,
)


def _approval():
    return build_reconciliation_approval(
        project_id="project-v1:example",
        workflow="NEXT_DOCS_PLAN",
        candidate_inputs=(("path", "docs/NEXT.md"),),
        git_head="0123456789abcdef",
        git_branch="main",
        policy_fingerprint="policy-sha256:abc",
    )


def _context() -> ReconciliationApprovalContext:
    approval = _approval()
    return ReconciliationApprovalContext(
        project_id=approval.project_id,
        workflow=approval.workflow,
        candidate_inputs=approval.candidate_inputs,
        git_head=approval.git_head,
        git_branch=approval.git_branch,
        policy_fingerprint=approval.policy_fingerprint,
    )


def test_exact_fresh_context_is_approved() -> None:
    result = verify_reconciliation_approval(_approval(), _context())

    assert result.state == "approved"
    assert result.mismatches == ()


def test_candidate_input_order_is_canonical() -> None:
    approval = build_reconciliation_approval(
        project_id="project-v1:example",
        workflow="NEXT_DOCS_PLAN",
        candidate_inputs=(("b", "2"), ("a", "1")),
        git_head="head",
        git_branch="main",
    )
    context = ReconciliationApprovalContext(
        project_id=approval.project_id,
        workflow=approval.workflow,
        candidate_inputs=(("a", "1"), ("b", "2")),
        git_head=approval.git_head,
        git_branch=approval.git_branch,
        policy_fingerprint=None,
    )

    assert verify_reconciliation_approval(approval, context).state == "approved"


def test_candidate_drift_fails_closed() -> None:
    context = replace(_context(), workflow="NEXT_OWNERSHIP_PLAN")

    result = verify_reconciliation_approval(_approval(), context)

    assert result.state == "approval_refused"
    assert [item.code for item in result.mismatches] == ["APPROVAL_CANDIDATE_MISMATCH"]


def test_git_drift_fails_closed() -> None:
    context = replace(_context(), git_head="new-head", git_branch="release")

    result = verify_reconciliation_approval(_approval(), context)

    assert result.state == "approval_refused"
    assert [item.code for item in result.mismatches] == [
        "APPROVAL_GIT_MISMATCH",
        "APPROVAL_GIT_MISMATCH",
    ]


def test_policy_drift_fails_closed() -> None:
    context = replace(_context(), policy_fingerprint="policy-sha256:different")

    result = verify_reconciliation_approval(_approval(), context)

    assert result.state == "approval_refused"
    assert [item.code for item in result.mismatches] == ["APPROVAL_POLICY_MISMATCH"]


def test_project_drift_fails_closed() -> None:
    context = replace(_context(), project_id="project-v1:other")

    result = verify_reconciliation_approval(_approval(), context)

    assert result.state == "approval_refused"
    assert [item.code for item in result.mismatches] == ["APPROVAL_PROJECT_MISMATCH"]


def test_multiple_mismatches_have_deterministic_order() -> None:
    context = replace(
        _context(),
        project_id="other",
        workflow="other-workflow",
        git_head="other-head",
        policy_fingerprint=None,
    )

    result = verify_reconciliation_approval(_approval(), context)

    assert result.state == "approval_refused"
    assert [item.code for item in result.mismatches] == [
        "APPROVAL_CANDIDATE_MISMATCH",
        "APPROVAL_GIT_MISMATCH",
        "APPROVAL_POLICY_MISMATCH",
        "APPROVAL_PROJECT_MISMATCH",
    ]


def test_verification_is_pure_and_repeatable() -> None:
    approval = _approval()
    context = _context()

    first = verify_reconciliation_approval(approval, context)
    second = verify_reconciliation_approval(approval, context)

    assert first == second
    assert approval == _approval()
    assert context == _context()
