"""Typed public-safe diagnostics for read-only control-plane hardening."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum

from .opencode_control_protocol import ControlProtocolError, ControlTaskClass

_REQUEST_ID_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class ControlFailureKind(str, Enum):
    """Stable top-level failure taxonomy for read-only control diagnostics."""

    TRANSPORT_READ_FAILURE = "transport_read_failure"
    PROTOCOL_REJECTION = "protocol_rejection"
    UNSUPPORTED_REQUEST = "unsupported_request"
    EXPECTED_HEAD_MISMATCH = "expected_head_mismatch"
    REPOSITORY_SNAPSHOT_FAILURE = "repository_snapshot_failure"
    EXECUTOR_FAILURE = "executor_failure"
    QUALITY_VERIFICATION_FAILURE = "quality_verification_failure"
    CLAIM_RECOVERY_REQUIRED = "claim_recovery_required"
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


class ClaimRecoveryReason(str, Enum):
    """Stable reason codes for fail-closed claim terminalization."""

    CLAIMED_WITHOUT_TERMINAL_RESULT = "claimed_without_terminal_result"


@dataclass(frozen=True, slots=True)
class ProtocolRejectionEvidence:
    """Bounded diagnostic evidence that never carries raw request content."""

    comment_id: int
    reason: ProtocolRejectionReason
    kind: ControlFailureKind = ControlFailureKind.PROTOCOL_REJECTION

    def __post_init__(self) -> None:
        if isinstance(self.comment_id, bool) or self.comment_id <= 0:
            raise ValueError("comment_id must be a positive integer")


@dataclass(frozen=True, slots=True)
class ClaimRecoveryEvidence:
    """Bounded public-safe evidence for an unresolved claimed request."""

    request_id: str
    task_class: ControlTaskClass
    repository: str
    reason: ClaimRecoveryReason = ClaimRecoveryReason.CLAIMED_WITHOUT_TERMINAL_RESULT
    replay_attempted: bool = False
    kind: ControlFailureKind = ControlFailureKind.CLAIM_RECOVERY_REQUIRED

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not _REQUEST_ID_RE.fullmatch(
            self.request_id
        ):
            raise ValueError("request_id must be a canonical sha256 identifier")
        if not isinstance(self.task_class, ControlTaskClass):
            raise ValueError("task_class must be a ControlTaskClass")
        if not isinstance(self.repository, str) or not _REPOSITORY_RE.fullmatch(
            self.repository
        ):
            raise ValueError("repository must be owner/name")
        if self.replay_attempted:
            raise ValueError("claim recovery evidence must never report replay")


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


def claim_recovery_evidence(
    *,
    request_id: str,
    task_class: ControlTaskClass,
    repository: str,
) -> ClaimRecoveryEvidence:
    """Build deterministic no-replay evidence for an unresolved visible claim."""

    return ClaimRecoveryEvidence(
        request_id=request_id,
        task_class=task_class,
        repository=repository,
    )


def serialize_claim_recovery(evidence: ClaimRecoveryEvidence) -> str:
    """Serialize bounded machine-stable claim-recovery evidence."""

    return json.dumps(
        {
            "kind": evidence.kind.value,
            "reason": evidence.reason.value,
            "replay_attempted": evidence.replay_attempted,
            "repository": evidence.repository,
            "request_id": evidence.request_id,
            "task_class": evidence.task_class.value,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
