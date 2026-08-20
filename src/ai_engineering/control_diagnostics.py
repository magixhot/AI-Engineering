"""Typed public-safe diagnostics for read-only control-plane hardening."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

from .opencode_control_protocol import ControlProtocolError


class ControlFailureKind(str, Enum):
    """Stable top-level failure taxonomy for AUTO-0018 diagnostics."""

    TRANSPORT_READ_FAILURE = "transport_read_failure"
    PROTOCOL_REJECTION = "protocol_rejection"
    UNSUPPORTED_REQUEST = "unsupported_request"
    EXPECTED_HEAD_MISMATCH = "expected_head_mismatch"
    REPOSITORY_SNAPSHOT_FAILURE = "repository_snapshot_failure"
    EXECUTOR_FAILURE = "executor_failure"
    QUALITY_VERIFICATION_FAILURE = "quality_verification_failure"
    SUCCESS = "success"


class ProtocolRejectionReason(str, Enum):
    """Stable reason codes for fail-closed request rejection."""

    MALFORMED_JSON = "malformed_json"
    NON_OBJECT_DOCUMENT = "non_object_document"
    SCHEMA_MISMATCH = "schema_mismatch"
    UNSUPPORTED_VERSION = "unsupported_version"
    UNKNOWN_TASK_CLASS = "unknown_task_class"
    INVALID_REQUEST_ID = "invalid_request_id"
    CANONICAL_REQUEST_ID_MISMATCH = "canonical_request_id_mismatch"
    INVALID_FIELD = "invalid_field"


@dataclass(frozen=True, slots=True)
class ProtocolRejectionEvidence:
    """Bounded diagnostic evidence that never carries raw request content."""

    comment_id: int
    reason: ProtocolRejectionReason
    kind: ControlFailureKind = ControlFailureKind.PROTOCOL_REJECTION

    def __post_init__(self) -> None:
        if isinstance(self.comment_id, bool) or self.comment_id <= 0:
            raise ValueError("comment_id must be a positive integer")


def classify_protocol_rejection(
    exc: ControlProtocolError,
) -> ProtocolRejectionReason:
    """Map current protocol failures to deterministic public-safe reason codes."""

    message = str(exc)
    exact = {
        "malformed JSON": ProtocolRejectionReason.MALFORMED_JSON,
        "protocol document must be a JSON object": (
            ProtocolRejectionReason.NON_OBJECT_DOCUMENT
        ),
        "request fields do not match protocol schema": (
            ProtocolRejectionReason.SCHEMA_MISMATCH
        ),
        "unknown task class": ProtocolRejectionReason.UNKNOWN_TASK_CLASS,
        "invalid request_id format": ProtocolRejectionReason.INVALID_REQUEST_ID,
        "request_id does not match canonical request payload": (
            ProtocolRejectionReason.CANONICAL_REQUEST_ID_MISMATCH
        ),
    }
    if message in exact:
        return exact[message]
    if message.startswith("unsupported protocol version: "):
        return ProtocolRejectionReason.UNSUPPORTED_VERSION
    return ProtocolRejectionReason.INVALID_FIELD


def protocol_rejection_evidence(
    *,
    comment_id: int,
    exc: ControlProtocolError,
) -> ProtocolRejectionEvidence:
    """Build typed rejection evidence without retaining exception/request text."""

    return ProtocolRejectionEvidence(
        comment_id=comment_id,
        reason=classify_protocol_rejection(exc),
    )


def serialize_protocol_rejection(evidence: ProtocolRejectionEvidence) -> str:
    """Serialize only bounded safe fields for logs or future control evidence."""

    return json.dumps(
        {
            "comment_id": evidence.comment_id,
            "kind": evidence.kind.value,
            "reason": evidence.reason.value,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
