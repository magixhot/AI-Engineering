from __future__ import annotations

import pytest

from ai_engineering.quality_verification import (
    QualityVerificationError,
    QualityVerificationState,
    build_verification_input,
    classify_exact_run,
    parse_workflow_run_evidence,
)

SHA = "0123456789abcdef0123456789abcdef01234567"


def _run(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "id": 123,
        "workflow_id": 456,
        "head_branch": "master",
        "head_sha": SHA,
        "event": "push",
        "status": "completed",
        "conclusion": "success",
        "run_attempt": 1,
    }
    value.update(overrides)
    return value


def test_build_verification_input_accepts_only_exact_supported_tuple() -> None:
    value = build_verification_input(repository="magixhot/AI-Engineering", head_sha=SHA)
    assert value.repository == "magixhot/AI-Engineering"
    assert value.branch == "master"
    assert value.workflow_path == ".github/workflows/quality.yml"
    assert value.event == "push"


@pytest.mark.parametrize(
    ("repository", "head_sha"),
    [
        ("missing-slash", SHA),
        ("owner/repo", "abc"),
        ("owner/repo", SHA.upper()),
    ],
)
def test_build_verification_input_rejects_invalid_identity(
    repository: str, head_sha: str
) -> None:
    with pytest.raises(QualityVerificationError):
        build_verification_input(repository=repository, head_sha=head_sha)


def test_parse_workflow_run_evidence_projects_only_typed_fields() -> None:
    raw = _run(token="must-not-survive", extra={"secret": "no"})
    evidence = parse_workflow_run_evidence(raw)
    assert evidence.run_id == 123
    assert evidence.workflow_id == 456
    assert evidence.run_attempt == 1
    assert not hasattr(evidence, "token")
    assert not hasattr(evidence, "extra")


@pytest.mark.parametrize(
    "field",
    [
        "id",
        "workflow_id",
        "head_branch",
        "head_sha",
        "event",
        "status",
        "conclusion",
    ],
)
def test_parse_workflow_run_evidence_rejects_missing_required_fields(
    field: str,
) -> None:
    raw = _run()
    del raw[field]
    with pytest.raises(QualityVerificationError):
        parse_workflow_run_evidence(raw)


def test_exact_completed_success_satisfies_gate() -> None:
    verification_input = build_verification_input(
        repository="magixhot/AI-Engineering", head_sha=SHA
    )
    result = classify_exact_run(verification_input, parse_workflow_run_evidence(_run()))
    assert result.state is QualityVerificationState.SUCCEEDED
    assert result.satisfies_gate is True


@pytest.mark.parametrize(
    "status",
    ["queued", "in_progress", "waiting", "requested", "pending"],
)
def test_nonterminal_exact_run_is_pending(status: str) -> None:
    verification_input = build_verification_input(
        repository="magixhot/AI-Engineering", head_sha=SHA
    )
    evidence = parse_workflow_run_evidence(_run(status=status, conclusion=None))
    result = classify_exact_run(verification_input, evidence)
    assert result.state is QualityVerificationState.PENDING
    assert result.satisfies_gate is False


@pytest.mark.parametrize(
    "conclusion",
    [
        "action_required",
        "cancelled",
        "failure",
        "neutral",
        "skipped",
        "stale",
        "startup_failure",
        "timed_out",
    ],
)
def test_terminal_non_success_fails_closed(conclusion: str) -> None:
    verification_input = build_verification_input(
        repository="magixhot/AI-Engineering", head_sha=SHA
    )
    result = classify_exact_run(
        verification_input, parse_workflow_run_evidence(_run(conclusion=conclusion))
    )
    assert result.state is QualityVerificationState.FAILED
    assert result.satisfies_gate is False


@pytest.mark.parametrize(
    "overrides",
    [
        {"head_branch": "feature"},
        {"head_sha": "fedcba9876543210fedcba9876543210fedcba98"},
        {"event": "pull_request"},
        {"status": "mystery", "conclusion": None},
        {"status": "completed", "conclusion": None},
    ],
)
def test_identity_or_schema_mismatch_is_invalid(
    overrides: dict[str, object],
) -> None:
    verification_input = build_verification_input(
        repository="magixhot/AI-Engineering", head_sha=SHA
    )
    result = classify_exact_run(
        verification_input, parse_workflow_run_evidence(_run(**overrides))
    )
    assert result.state is QualityVerificationState.INVALID
    assert result.satisfies_gate is False


def test_nonterminal_run_with_conclusion_is_invalid() -> None:
    verification_input = build_verification_input(
        repository="magixhot/AI-Engineering", head_sha=SHA
    )
    evidence = parse_workflow_run_evidence(
        _run(status="in_progress", conclusion="success")
    )
    result = classify_exact_run(verification_input, evidence)
    assert result.state is QualityVerificationState.INVALID
