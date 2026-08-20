from __future__ import annotations

import json

import pytest

from ai_engineering.control_diagnostics import (
    ClaimRecoveryEvidence,
    ClaimRecoveryReason,
    ControlFailureKind,
    ProtocolRejectionEvidence,
    ProtocolRejectionReason,
    claim_recovery_evidence,
    classify_protocol_rejection,
    protocol_rejection_evidence,
    serialize_claim_recovery,
    serialize_protocol_rejection,
)
from ai_engineering.opencode_control_protocol import (
    ControlProtocolError,
    ControlTaskClass,
)


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("malformed JSON", ProtocolRejectionReason.MALFORMED_JSON),
        (
            "protocol document must be a JSON object",
            ProtocolRejectionReason.NON_OBJECT_DOCUMENT,
        ),
        (
            "request fields do not match protocol schema",
            ProtocolRejectionReason.SCHEMA_MISMATCH,
        ),
        (
            "unsupported protocol version: 2",
            ProtocolRejectionReason.UNSUPPORTED_VERSION,
        ),
        ("unknown task class", ProtocolRejectionReason.UNKNOWN_TASK_CLASS),
        ("invalid request_id format", ProtocolRejectionReason.INVALID_REQUEST_ID),
        (
            "request_id does not match canonical request payload",
            ProtocolRejectionReason.CANONICAL_REQUEST_ID_MISMATCH,
        ),
        ("objective must not be empty", ProtocolRejectionReason.INVALID_FIELD),
    ],
)
def test_classify_protocol_rejection_is_deterministic(
    message: str,
    expected: ProtocolRejectionReason,
) -> None:
    assert classify_protocol_rejection(ControlProtocolError(message)) is expected


def test_protocol_rejection_evidence_contains_only_bounded_safe_fields() -> None:
    evidence = protocol_rejection_evidence(
        comment_id=12345,
        exc=ControlProtocolError(
            "private local path /home/example and token=secret must never leak"
        ),
    )

    encoded = serialize_protocol_rejection(evidence)
    payload = json.loads(encoded)

    assert payload == {
        "comment_id": 12345,
        "kind": ControlFailureKind.PROTOCOL_REJECTION.value,
        "reason": ProtocolRejectionReason.INVALID_FIELD.value,
    }
    assert "/home/example" not in encoded
    assert "secret" not in encoded


def test_protocol_rejection_evidence_rejects_invalid_comment_id() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        ProtocolRejectionEvidence(
            comment_id=0,
            reason=ProtocolRejectionReason.MALFORMED_JSON,
        )


def test_claim_recovery_evidence_is_bounded_public_safe_and_no_replay() -> None:
    request_id = "sha256:" + "a" * 64
    evidence = claim_recovery_evidence(
        request_id=request_id,
        task_class=ControlTaskClass.INSPECT,
        repository="magixhot/AI-Engineering",
    )

    encoded = serialize_claim_recovery(evidence)
    payload = json.loads(encoded)

    assert payload == {
        "kind": ControlFailureKind.CLAIM_RECOVERY_REQUIRED.value,
        "reason": ClaimRecoveryReason.CLAIMED_WITHOUT_TERMINAL_RESULT.value,
        "replay_attempted": False,
        "repository": "magixhot/AI-Engineering",
        "request_id": request_id,
        "task_class": "inspect",
    }
    assert len(encoded) < 512
    assert "/home/" not in encoded
    assert "C:\\" not in encoded
    assert "objective" not in encoded


def test_claim_recovery_evidence_rejects_noncanonical_identity() -> None:
    with pytest.raises(ValueError, match="canonical sha256"):
        ClaimRecoveryEvidence(
            request_id="not-canonical",
            task_class=ControlTaskClass.STATUS,
            repository="magixhot/AI-Engineering",
        )

    with pytest.raises(ValueError, match="owner/name"):
        ClaimRecoveryEvidence(
            request_id="sha256:" + "b" * 64,
            task_class=ControlTaskClass.STATUS,
            repository="private local path",
        )


def test_claim_recovery_evidence_cannot_report_replay() -> None:
    with pytest.raises(ValueError, match="must never report replay"):
        ClaimRecoveryEvidence(
            request_id="sha256:" + "c" * 64,
            task_class=ControlTaskClass.DIFF,
            repository="magixhot/AI-Engineering",
            replay_attempted=True,
        )


def test_failure_taxonomy_includes_all_design_required_categories() -> None:
    assert {item.value for item in ControlFailureKind} == {
        "transport_read_failure",
        "protocol_rejection",
        "unsupported_request",
        "expected_head_mismatch",
        "repository_snapshot_failure",
        "executor_failure",
        "quality_verification_failure",
        "claim_recovery_required",
        "success",
    }
