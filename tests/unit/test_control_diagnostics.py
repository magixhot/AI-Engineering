from __future__ import annotations

import json

import pytest

from ai_engineering.control_diagnostics import (
    ControlFailureKind,
    ProtocolRejectionEvidence,
    ProtocolRejectionReason,
    classify_protocol_rejection,
    protocol_rejection_evidence,
    serialize_protocol_rejection,
)
from ai_engineering.opencode_control_protocol import ControlProtocolError


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


def test_failure_taxonomy_includes_all_design_required_categories() -> None:
    assert {item.value for item in ControlFailureKind} == {
        "transport_read_failure",
        "protocol_rejection",
        "unsupported_request",
        "expected_head_mismatch",
        "repository_snapshot_failure",
        "executor_failure",
        "quality_verification_failure",
        "success",
    }
