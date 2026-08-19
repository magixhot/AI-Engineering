from __future__ import annotations

from dataclasses import replace

from ai_engineering.quality_verification import (
    QualityVerificationState,
    WorkflowRunEvidence,
    build_verification_input,
)
from ai_engineering.quality_verifier import select_authoritative_run

SHA = "0123456789abcdef0123456789abcdef01234567"


def _run(
    *,
    run_id: int = 10,
    run_attempt: int | None = 1,
    status: str = "completed",
    conclusion: str | None = "success",
) -> WorkflowRunEvidence:
    return WorkflowRunEvidence(
        run_id=run_id,
        workflow_id=20,
        head_branch="master",
        head_sha=SHA,
        event="push",
        status=status,
        conclusion=conclusion,
        run_attempt=run_attempt,
    )


def _input():
    return build_verification_input(
        repository="magixhot/AI-Engineering",
        head_sha=SHA,
    )


def test_no_run_is_pending() -> None:
    result = select_authoritative_run(_input(), [])
    assert result.state is QualityVerificationState.PENDING
    assert result.satisfies_gate is False


def test_one_exact_success_run_succeeds() -> None:
    result = select_authoritative_run(_input(), [_run()])
    assert result.state is QualityVerificationState.SUCCEEDED
    assert result.satisfies_gate is True


def test_distinct_exact_run_ids_are_ambiguous() -> None:
    result = select_authoritative_run(_input(), [_run(run_id=10), _run(run_id=11)])
    assert result.state is QualityVerificationState.AMBIGUOUS


def test_highest_attempt_of_same_run_id_is_authoritative() -> None:
    failed = _run(run_attempt=1, conclusion="failure")
    succeeded = _run(run_attempt=2, conclusion="success")
    result = select_authoritative_run(_input(), [failed, succeeded])
    assert result.state is QualityVerificationState.SUCCEEDED
    assert result.evidence == succeeded


def test_multiple_records_without_attempt_are_ambiguous() -> None:
    first = _run(run_attempt=None)
    second = replace(first, status="in_progress", conclusion=None)
    result = select_authoritative_run(_input(), [first, second])
    assert result.state is QualityVerificationState.AMBIGUOUS


def test_conflicting_same_attempt_is_ambiguous() -> None:
    first = _run(run_attempt=2, conclusion="failure")
    second = replace(first, conclusion="success")
    result = select_authoritative_run(_input(), [first, second])
    assert result.state is QualityVerificationState.AMBIGUOUS


def test_wrong_exact_identity_is_invalid() -> None:
    wrong = replace(_run(), event="pull_request")
    result = select_authoritative_run(_input(), [wrong])
    assert result.state is QualityVerificationState.INVALID


def test_pending_highest_attempt_remains_pending() -> None:
    completed = _run(run_attempt=1, conclusion="success")
    pending = _run(run_attempt=2, status="in_progress", conclusion=None)
    result = select_authoritative_run(_input(), [completed, pending])
    assert result.state is QualityVerificationState.PENDING
    assert result.evidence == pending
