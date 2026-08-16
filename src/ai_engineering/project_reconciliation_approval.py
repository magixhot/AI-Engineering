"""Typed deterministic reconciliation approval artifacts for AUTO-0011."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Literal

ApprovalLoadState = Literal["loaded", "approval_error"]

_APPROVAL_VERSION = 1
_ALLOWED_FIELDS = frozenset(
    {
        "version",
        "project_id",
        "workflow",
        "candidate_inputs",
        "git_head",
        "git_branch",
        "policy_fingerprint",
        "scope",
        "digest",
    }
)


@dataclass(frozen=True)
class ReconciliationApprovalIssue:
    """Stable machine-readable approval artifact evidence."""

    code: str
    detail: str


@dataclass(frozen=True)
class ReconciliationApproval:
    """Validated single-candidate approval artifact."""

    version: int
    project_id: str
    workflow: str
    candidate_inputs: tuple[tuple[str, str], ...]
    git_head: str
    git_branch: str | None
    policy_fingerprint: str | None
    scope: str
    digest: str


@dataclass(frozen=True)
class ReconciliationApprovalLoadResult:
    """Result of strict approval JSON parsing and digest validation."""

    state: ApprovalLoadState
    approval: ReconciliationApproval | None
    issues: tuple[ReconciliationApprovalIssue, ...]


def _issue(code: str, detail: str) -> ReconciliationApprovalIssue:
    return ReconciliationApprovalIssue(code=code, detail=detail)


def _error(*issues: ReconciliationApprovalIssue) -> ReconciliationApprovalLoadResult:
    return ReconciliationApprovalLoadResult(
        state="approval_error",
        approval=None,
        issues=tuple(sorted(issues, key=lambda item: (item.code, item.detail))),
    )


def _canonical_payload(
    *,
    version: int,
    project_id: str,
    workflow: str,
    candidate_inputs: tuple[tuple[str, str], ...],
    git_head: str,
    git_branch: str | None,
    policy_fingerprint: str | None,
    scope: str,
) -> dict[str, object]:
    return {
        "candidate_inputs": {key: value for key, value in candidate_inputs},
        "git_branch": git_branch,
        "git_head": git_head,
        "policy_fingerprint": policy_fingerprint,
        "project_id": project_id,
        "scope": scope,
        "version": version,
        "workflow": workflow,
    }


def canonical_approval_payload_bytes(
    *,
    version: int,
    project_id: str,
    workflow: str,
    candidate_inputs: tuple[tuple[str, str], ...],
    git_head: str,
    git_branch: str | None,
    policy_fingerprint: str | None,
    scope: str = "single_candidate",
) -> bytes:
    """Serialize authority-relevant fields with one deterministic JSON encoding."""

    payload = _canonical_payload(
        version=version,
        project_id=project_id,
        workflow=workflow,
        candidate_inputs=tuple(sorted(candidate_inputs)),
        git_head=git_head,
        git_branch=git_branch,
        policy_fingerprint=policy_fingerprint,
        scope=scope,
    )
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def approval_digest(**kwargs: object) -> str:
    """Return the lowercase SHA-256 digest of a canonical approval payload."""

    return hashlib.sha256(canonical_approval_payload_bytes(**kwargs)).hexdigest()


def build_reconciliation_approval(
    *,
    project_id: str,
    workflow: str,
    candidate_inputs: tuple[tuple[str, str], ...],
    git_head: str,
    git_branch: str | None,
    policy_fingerprint: str | None = None,
) -> ReconciliationApproval:
    """Build one deterministic, single-candidate approval artifact."""

    inputs = tuple(sorted(candidate_inputs))
    fields = {
        "version": _APPROVAL_VERSION,
        "project_id": project_id,
        "workflow": workflow,
        "candidate_inputs": inputs,
        "git_head": git_head,
        "git_branch": git_branch,
        "policy_fingerprint": policy_fingerprint,
        "scope": "single_candidate",
    }
    digest = approval_digest(**fields)
    return ReconciliationApproval(digest=digest, **fields)


def serialize_reconciliation_approval(approval: ReconciliationApproval) -> bytes:
    """Serialize a validated approval including its digest deterministically."""

    payload = _canonical_payload(
        version=approval.version,
        project_id=approval.project_id,
        workflow=approval.workflow,
        candidate_inputs=approval.candidate_inputs,
        git_head=approval.git_head,
        git_branch=approval.git_branch,
        policy_fingerprint=approval.policy_fingerprint,
        scope=approval.scope,
    )
    payload["digest"] = approval.digest
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def parse_reconciliation_approval(raw: bytes) -> ReconciliationApprovalLoadResult:
    """Strictly parse JSON, reject unknowns, and verify the bound digest."""

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _error(
            _issue(
                "APPROVAL_PARSE_ERROR",
                "approval JSON could not be parsed",
            )
        )
    if not isinstance(data, dict):
        return _error(_issue("APPROVAL_ROOT_TYPE", "approval root must be an object"))

    unknown = sorted(set(data) - _ALLOWED_FIELDS)
    missing = sorted(_ALLOWED_FIELDS - set(data))
    issues: list[ReconciliationApprovalIssue] = []
    issues.extend(
        _issue("APPROVAL_UNKNOWN_FIELD", f"unknown approval field: {field}")
        for field in unknown
    )
    issues.extend(
        _issue("APPROVAL_MISSING_FIELD", f"missing approval field: {field}")
        for field in missing
    )
    if issues:
        return _error(*issues)

    if type(data["version"]) is not int or data["version"] != _APPROVAL_VERSION:
        issues.append(
            _issue("APPROVAL_VERSION_UNSUPPORTED", "approval version must be integer 1")
        )
    for field in ("project_id", "workflow", "git_head", "scope", "digest"):
        if not isinstance(data[field], str) or not data[field]:
            issues.append(
                _issue(
                    "APPROVAL_FIELD_TYPE",
                    f"{field} must be a non-empty string",
                )
            )
    for field in ("git_branch", "policy_fingerprint"):
        if data[field] is not None and not isinstance(data[field], str):
            issues.append(
                _issue(
                    "APPROVAL_FIELD_TYPE",
                    f"{field} must be a string or null",
                )
            )
    if data["scope"] != "single_candidate":
        issues.append(
            _issue(
                "APPROVAL_SCOPE_INVALID",
                "scope must be single_candidate",
            )
        )

    raw_inputs = data["candidate_inputs"]
    candidate_inputs: tuple[tuple[str, str], ...] = ()
    if not isinstance(raw_inputs, dict) or any(
        not isinstance(key, str) or not isinstance(value, str)
        for key, value in raw_inputs.items()
    ):
        issues.append(
            _issue(
                "APPROVAL_FIELD_TYPE",
                "candidate_inputs must be an object of string keys and values",
            )
        )
    else:
        candidate_inputs = tuple(sorted(raw_inputs.items()))

    if issues:
        return _error(*issues)

    version = data["version"]
    project_id = data["project_id"]
    workflow = data["workflow"]
    git_head = data["git_head"]
    git_branch = data["git_branch"]
    policy_fingerprint = data["policy_fingerprint"]
    scope = data["scope"]
    digest = data["digest"]
    expected = approval_digest(
        version=version,
        project_id=project_id,
        workflow=workflow,
        candidate_inputs=candidate_inputs,
        git_head=git_head,
        git_branch=git_branch,
        policy_fingerprint=policy_fingerprint,
        scope=scope,
    )
    if digest != expected:
        return _error(
            _issue(
                "APPROVAL_DIGEST_INVALID",
                "approval digest does not match payload",
            )
        )

    return ReconciliationApprovalLoadResult(
        state="loaded",
        approval=ReconciliationApproval(
            version=version,
            project_id=project_id,
            workflow=workflow,
            candidate_inputs=candidate_inputs,
            git_head=git_head,
            git_branch=git_branch,
            policy_fingerprint=policy_fingerprint,
            scope=scope,
            digest=digest,
        ),
        issues=(),
    )
