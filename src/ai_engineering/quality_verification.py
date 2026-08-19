"""Typed, fail-closed evidence model for AUTO-0015 post-merge Quality verification."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

EXPECTED_BRANCH = "master"
EXPECTED_EVENT = "push"
EXPECTED_WORKFLOW_PATH = ".github/workflows/quality.yml"
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_TERMINAL_NON_SUCCESS_CONCLUSIONS = frozenset(
    {
        "action_required",
        "cancelled",
        "failure",
        "neutral",
        "skipped",
        "stale",
        "startup_failure",
        "timed_out",
    }
)


class QualityVerificationError(ValueError):
    """Raised when exact Quality verification evidence violates the contract."""


class QualityVerificationState(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class QualityVerificationInput:
    repository: str
    head_sha: str
    branch: str = EXPECTED_BRANCH
    workflow_path: str = EXPECTED_WORKFLOW_PATH
    event: str = EXPECTED_EVENT


@dataclass(frozen=True, slots=True)
class WorkflowRunEvidence:
    run_id: int
    workflow_id: int
    head_branch: str
    head_sha: str
    event: str
    status: str
    conclusion: str | None
    run_attempt: int | None = None


@dataclass(frozen=True, slots=True)
class QualityVerificationResult:
    state: QualityVerificationState
    verification_input: QualityVerificationInput
    evidence: WorkflowRunEvidence | None = None
    reason: str | None = None

    @property
    def satisfies_gate(self) -> bool:
        return self.state is QualityVerificationState.SUCCEEDED


def validate_verification_input(value: QualityVerificationInput) -> None:
    if not isinstance(value.repository, str) or not _REPOSITORY_RE.fullmatch(
        value.repository
    ):
        raise QualityVerificationError("repository must be owner/name")
    if not isinstance(value.head_sha, str) or not _SHA_RE.fullmatch(value.head_sha):
        raise QualityVerificationError(
            "head_sha must be a lowercase 40-character commit SHA"
        )
    if value.branch != EXPECTED_BRANCH:
        raise QualityVerificationError("unsupported verification branch")
    if value.workflow_path != EXPECTED_WORKFLOW_PATH:
        raise QualityVerificationError("unsupported workflow path")
    if value.event != EXPECTED_EVENT:
        raise QualityVerificationError("unsupported verification event")


def build_verification_input(*, repository: str, head_sha: str) -> QualityVerificationInput:
    value = QualityVerificationInput(repository=repository, head_sha=head_sha)
    validate_verification_input(value)
    return value


def _require_positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise QualityVerificationError(f"{field} must be a positive integer")
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise QualityVerificationError(f"{field} must be a non-empty string")
    return value


def parse_workflow_run_evidence(value: Mapping[str, Any]) -> WorkflowRunEvidence:
    """Project one workflow-run object into bounded typed evidence."""

    if not isinstance(value, Mapping):
        raise QualityVerificationError("workflow run must be an object")
    required = {
        "id",
        "workflow_id",
        "head_branch",
        "head_sha",
        "event",
        "status",
        "conclusion",
    }
    if not required.issubset(value):
        raise QualityVerificationError("workflow run is missing required fields")

    run_attempt_raw = value.get("run_attempt")
    run_attempt = None
    if run_attempt_raw is not None:
        run_attempt = _require_positive_int(run_attempt_raw, "run_attempt")

    head_sha = _require_string(value["head_sha"], "head_sha")
    if not _SHA_RE.fullmatch(head_sha):
        raise QualityVerificationError(
            "workflow run head_sha must be a lowercase 40-character SHA"
        )

    conclusion_raw = value["conclusion"]
    if conclusion_raw is not None and not isinstance(conclusion_raw, str):
        raise QualityVerificationError("conclusion must be a string or null")

    return WorkflowRunEvidence(
        run_id=_require_positive_int(value["id"], "id"),
        workflow_id=_require_positive_int(value["workflow_id"], "workflow_id"),
        head_branch=_require_string(value["head_branch"], "head_branch"),
        head_sha=head_sha,
        event=_require_string(value["event"], "event"),
        status=_require_string(value["status"], "status"),
        conclusion=conclusion_raw,
        run_attempt=run_attempt,
    )


def classify_exact_run(
    verification_input: QualityVerificationInput,
    evidence: WorkflowRunEvidence,
) -> QualityVerificationResult:
    """Classify one already-selected run against the immutable exact tuple."""

    validate_verification_input(verification_input)
    if evidence.head_branch != verification_input.branch:
        return QualityVerificationResult(
            QualityVerificationState.INVALID,
            verification_input,
            evidence,
            "workflow run branch does not match expected branch",
        )
    if evidence.head_sha != verification_input.head_sha:
        return QualityVerificationResult(
            QualityVerificationState.INVALID,
            verification_input,
            evidence,
            "workflow run head_sha does not match exact expected SHA",
        )
    if evidence.event != verification_input.event:
        return QualityVerificationResult(
            QualityVerificationState.INVALID,
            verification_input,
            evidence,
            "workflow run event does not match expected event",
        )

    if evidence.status in {"queued", "in_progress", "waiting", "requested", "pending"}:
        if evidence.conclusion is not None:
            return QualityVerificationResult(
                QualityVerificationState.INVALID,
                verification_input,
                evidence,
                "non-completed workflow run has a conclusion",
            )
        return QualityVerificationResult(
            QualityVerificationState.PENDING, verification_input, evidence
        )

    if evidence.status != "completed":
        return QualityVerificationResult(
            QualityVerificationState.INVALID,
            verification_input,
            evidence,
            "unsupported workflow run status",
        )
    if evidence.conclusion == "success":
        return QualityVerificationResult(
            QualityVerificationState.SUCCEEDED, verification_input, evidence
        )
    if evidence.conclusion in _TERMINAL_NON_SUCCESS_CONCLUSIONS:
        return QualityVerificationResult(
            QualityVerificationState.FAILED, verification_input, evidence
        )
    return QualityVerificationResult(
        QualityVerificationState.INVALID,
        verification_input,
        evidence,
        "completed workflow run has an unsupported conclusion",
    )
