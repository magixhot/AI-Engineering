"""Typed deterministic reconciliation execution receipts for AUTO-0012."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Literal

ReceiptLoadState = Literal["loaded", "receipt_error"]

_RECEIPT_VERSION = 1
_RECEIPT_KIND = "reconciliation_execution"
_ALLOWED_FIELDS = frozenset(
    {
        "version",
        "kind",
        "project_id",
        "requested_max_steps",
        "initial_state",
        "git_head",
        "git_branch",
        "policy_fingerprint",
        "approval_digest",
        "approval_scope",
        "policy_decisions",
        "approval_verifications",
        "attempts",
        "successful_steps",
        "terminal_state",
        "terminal_issues",
        "final_plan_state",
        "remaining_work",
        "digest",
    }
)


@dataclass(frozen=True)
class ReconciliationReceiptIssue:
    """Stable machine-readable receipt validation evidence."""

    code: str
    detail: str


@dataclass(frozen=True)
class ReceiptPolicyDecision:
    """Ordered policy decision evidence observed during one run."""

    workflow: str
    state: str
    effective_max_steps: int | None
    issues: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ReceiptApprovalVerification:
    """Ordered approval verification evidence observed during one run."""

    workflow: str
    state: str
    issues: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ReceiptApplyAttempt:
    """Ordered delegated AUTO-0008 apply-attempt evidence."""

    sequence: int
    workflow: str
    state: str
    write_attempted: bool
    delegated_subsystem: str | None
    rollback_status: str
    post_apply_state: str
    issues: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ReconciliationExecutionReceipt:
    """Validated immutable execution receipt."""

    version: int
    kind: str
    project_id: str
    requested_max_steps: int
    initial_state: str
    git_head: str
    git_branch: str | None
    policy_fingerprint: str | None
    approval_digest: str | None
    approval_scope: str | None
    policy_decisions: tuple[ReceiptPolicyDecision, ...]
    approval_verifications: tuple[ReceiptApprovalVerification, ...]
    attempts: tuple[ReceiptApplyAttempt, ...]
    successful_steps: int
    terminal_state: str
    terminal_issues: tuple[tuple[str, str], ...]
    final_plan_state: str
    remaining_work: tuple[tuple[str, str], ...]
    digest: str


@dataclass(frozen=True)
class ReconciliationReceiptLoadResult:
    """Result of strict receipt JSON parsing and digest validation."""

    state: ReceiptLoadState
    receipt: ReconciliationExecutionReceipt | None
    issues: tuple[ReconciliationReceiptIssue, ...]


def _issue(code: str, detail: str) -> ReconciliationReceiptIssue:
    return ReconciliationReceiptIssue(code=code, detail=detail)


def _error(*issues: ReconciliationReceiptIssue) -> ReconciliationReceiptLoadResult:
    return ReconciliationReceiptLoadResult(
        state="receipt_error",
        receipt=None,
        issues=tuple(sorted(issues, key=lambda item: (item.code, item.detail))),
    )


def _pairs_object(items: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
    return [{"code": code, "detail": detail} for code, detail in items]


def _policy_object(item: ReceiptPolicyDecision) -> dict[str, object]:
    return {
        "effective_max_steps": item.effective_max_steps,
        "issues": _pairs_object(tuple(sorted(item.issues))),
        "state": item.state,
        "workflow": item.workflow,
    }


def _approval_object(item: ReceiptApprovalVerification) -> dict[str, object]:
    return {
        "issues": _pairs_object(tuple(sorted(item.issues))),
        "state": item.state,
        "workflow": item.workflow,
    }


def _attempt_object(item: ReceiptApplyAttempt) -> dict[str, object]:
    return {
        "delegated_subsystem": item.delegated_subsystem,
        "issues": _pairs_object(tuple(sorted(item.issues))),
        "post_apply_state": item.post_apply_state,
        "rollback_status": item.rollback_status,
        "sequence": item.sequence,
        "state": item.state,
        "workflow": item.workflow,
        "write_attempted": item.write_attempted,
    }


def _canonical_payload(receipt: ReconciliationExecutionReceipt) -> dict[str, object]:
    return {
        "approval_digest": receipt.approval_digest,
        "approval_scope": receipt.approval_scope,
        "approval_verifications": [
            _approval_object(item) for item in receipt.approval_verifications
        ],
        "attempts": [_attempt_object(item) for item in receipt.attempts],
        "final_plan_state": receipt.final_plan_state,
        "git_branch": receipt.git_branch,
        "git_head": receipt.git_head,
        "initial_state": receipt.initial_state,
        "kind": receipt.kind,
        "policy_decisions": [_policy_object(item) for item in receipt.policy_decisions],
        "policy_fingerprint": receipt.policy_fingerprint,
        "project_id": receipt.project_id,
        "remaining_work": _pairs_object(tuple(sorted(receipt.remaining_work))),
        "requested_max_steps": receipt.requested_max_steps,
        "successful_steps": receipt.successful_steps,
        "terminal_issues": _pairs_object(tuple(sorted(receipt.terminal_issues))),
        "terminal_state": receipt.terminal_state,
        "version": receipt.version,
    }


def canonical_receipt_payload_bytes(receipt: ReconciliationExecutionReceipt) -> bytes:
    """Serialize receipt payload fields with one deterministic JSON encoding."""

    return json.dumps(
        _canonical_payload(receipt),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def reconciliation_receipt_digest(receipt: ReconciliationExecutionReceipt) -> str:
    """Return the lowercase SHA-256 digest of the canonical receipt payload."""

    return hashlib.sha256(canonical_receipt_payload_bytes(receipt)).hexdigest()


def build_reconciliation_execution_receipt(
    *,
    project_id: str,
    requested_max_steps: int,
    initial_state: str,
    git_head: str,
    git_branch: str | None,
    policy_fingerprint: str | None = None,
    approval_digest: str | None = None,
    approval_scope: str | None = None,
    policy_decisions: tuple[ReceiptPolicyDecision, ...] = (),
    approval_verifications: tuple[ReceiptApprovalVerification, ...] = (),
    attempts: tuple[ReceiptApplyAttempt, ...] = (),
    successful_steps: int = 0,
    terminal_state: str,
    terminal_issues: tuple[tuple[str, str], ...] = (),
    final_plan_state: str,
    remaining_work: tuple[tuple[str, str], ...] = (),
) -> ReconciliationExecutionReceipt:
    """Build one deterministic version-1 receipt from already-observed evidence."""

    receipt = ReconciliationExecutionReceipt(
        version=_RECEIPT_VERSION,
        kind=_RECEIPT_KIND,
        project_id=project_id,
        requested_max_steps=requested_max_steps,
        initial_state=initial_state,
        git_head=git_head,
        git_branch=git_branch,
        policy_fingerprint=policy_fingerprint,
        approval_digest=approval_digest,
        approval_scope=approval_scope,
        policy_decisions=policy_decisions,
        approval_verifications=approval_verifications,
        attempts=attempts,
        successful_steps=successful_steps,
        terminal_state=terminal_state,
        terminal_issues=tuple(sorted(terminal_issues)),
        final_plan_state=final_plan_state,
        remaining_work=tuple(sorted(remaining_work)),
        digest="",
    )
    digest = reconciliation_receipt_digest(receipt)
    return ReconciliationExecutionReceipt(**{**receipt.__dict__, "digest": digest})


def serialize_reconciliation_execution_receipt(
    receipt: ReconciliationExecutionReceipt,
) -> bytes:
    """Serialize a validated receipt including its digest deterministically."""

    payload = _canonical_payload(receipt)
    payload["digest"] = receipt.digest
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _parse_issue_pairs(value: object, field: str) -> tuple[tuple[str, str], ...] | None:
    if not isinstance(value, list):
        return None
    parsed: list[tuple[str, str]] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {"code", "detail"}:
            return None
        code = item.get("code")
        detail = item.get("detail")
        if not isinstance(code, str) or not isinstance(detail, str):
            return None
        parsed.append((code, detail))
    return tuple(parsed)


def _parse_policy_decisions(value: object) -> tuple[ReceiptPolicyDecision, ...] | None:
    if not isinstance(value, list):
        return None
    parsed: list[ReceiptPolicyDecision] = []
    expected = {"workflow", "state", "effective_max_steps", "issues"}
    for item in value:
        if not isinstance(item, dict) or set(item) != expected:
            return None
        workflow = item.get("workflow")
        state = item.get("state")
        limit = item.get("effective_max_steps")
        issues = _parse_issue_pairs(item.get("issues"), "issues")
        if (
            not isinstance(workflow, str)
            or not workflow
            or not isinstance(state, str)
            or not state
            or (limit is not None and type(limit) is not int)
            or issues is None
        ):
            return None
        parsed.append(
            ReceiptPolicyDecision(
                workflow=workflow,
                state=state,
                effective_max_steps=limit,
                issues=tuple(sorted(issues)),
            )
        )
    return tuple(parsed)


def _parse_approval_verifications(
    value: object,
) -> tuple[ReceiptApprovalVerification, ...] | None:
    if not isinstance(value, list):
        return None
    parsed: list[ReceiptApprovalVerification] = []
    expected = {"workflow", "state", "issues"}
    for item in value:
        if not isinstance(item, dict) or set(item) != expected:
            return None
        workflow = item.get("workflow")
        state = item.get("state")
        issues = _parse_issue_pairs(item.get("issues"), "issues")
        if (
            not isinstance(workflow, str)
            or not workflow
            or not isinstance(state, str)
            or not state
            or issues is None
        ):
            return None
        parsed.append(
            ReceiptApprovalVerification(
                workflow=workflow,
                state=state,
                issues=tuple(sorted(issues)),
            )
        )
    return tuple(parsed)


def _parse_attempts(value: object) -> tuple[ReceiptApplyAttempt, ...] | None:
    if not isinstance(value, list):
        return None
    parsed: list[ReceiptApplyAttempt] = []
    expected = {
        "sequence",
        "workflow",
        "state",
        "write_attempted",
        "delegated_subsystem",
        "rollback_status",
        "post_apply_state",
        "issues",
    }
    for item in value:
        if not isinstance(item, dict) or set(item) != expected:
            return None
        sequence = item.get("sequence")
        workflow = item.get("workflow")
        state = item.get("state")
        write_attempted = item.get("write_attempted")
        delegated = item.get("delegated_subsystem")
        rollback = item.get("rollback_status")
        post_apply = item.get("post_apply_state")
        issues = _parse_issue_pairs(item.get("issues"), "issues")
        if (
            type(sequence) is not int
            or sequence < 1
            or not isinstance(workflow, str)
            or not workflow
            or not isinstance(state, str)
            or not state
            or type(write_attempted) is not bool
            or (delegated is not None and not isinstance(delegated, str))
            or not isinstance(rollback, str)
            or not rollback
            or not isinstance(post_apply, str)
            or not post_apply
            or issues is None
        ):
            return None
        parsed.append(
            ReceiptApplyAttempt(
                sequence=sequence,
                workflow=workflow,
                state=state,
                write_attempted=write_attempted,
                delegated_subsystem=delegated,
                rollback_status=rollback,
                post_apply_state=post_apply,
                issues=tuple(sorted(issues)),
            )
        )
    return tuple(parsed)


def parse_reconciliation_execution_receipt(
    raw: bytes,
) -> ReconciliationReceiptLoadResult:
    """Strictly parse JSON, reject unknowns, and verify the receipt digest."""

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _error(_issue("RECEIPT_PARSE_ERROR", "receipt JSON could not be parsed"))
    if not isinstance(data, dict):
        return _error(_issue("RECEIPT_ROOT_TYPE", "receipt root must be an object"))

    unknown = sorted(set(data) - _ALLOWED_FIELDS)
    missing = sorted(_ALLOWED_FIELDS - set(data))
    issues: list[ReconciliationReceiptIssue] = []
    issues.extend(
        _issue("RECEIPT_UNKNOWN_FIELD", f"unknown receipt field: {field}")
        for field in unknown
    )
    issues.extend(
        _issue("RECEIPT_MISSING_FIELD", f"missing receipt field: {field}")
        for field in missing
    )
    if issues:
        return _error(*issues)

    if type(data["version"]) is not int or data["version"] != _RECEIPT_VERSION:
        issues.append(
            _issue("RECEIPT_VERSION_UNSUPPORTED", "receipt version must be integer 1")
        )
    if data["kind"] != _RECEIPT_KIND:
        issues.append(
            _issue("RECEIPT_KIND_INVALID", f"receipt kind must be {_RECEIPT_KIND}")
        )
    for field in (
        "project_id",
        "initial_state",
        "git_head",
        "terminal_state",
        "final_plan_state",
        "digest",
    ):
        if not isinstance(data[field], str) or not data[field]:
            issues.append(
                _issue("RECEIPT_FIELD_TYPE", f"{field} must be a non-empty string")
            )
    for field in (
        "git_branch",
        "policy_fingerprint",
        "approval_digest",
        "approval_scope",
    ):
        if data[field] is not None and not isinstance(data[field], str):
            issues.append(
                _issue("RECEIPT_FIELD_TYPE", f"{field} must be a string or null")
            )
    for field in ("requested_max_steps", "successful_steps"):
        if type(data[field]) is not int or data[field] < 0:
            issues.append(
                _issue("RECEIPT_FIELD_TYPE", f"{field} must be a non-negative integer")
            )

    policy_decisions = _parse_policy_decisions(data["policy_decisions"])
    approval_verifications = _parse_approval_verifications(
        data["approval_verifications"]
    )
    attempts = _parse_attempts(data["attempts"])
    terminal_issues = _parse_issue_pairs(data["terminal_issues"], "terminal_issues")
    remaining_work = _parse_issue_pairs(data["remaining_work"], "remaining_work")
    for field, parsed in (
        ("policy_decisions", policy_decisions),
        ("approval_verifications", approval_verifications),
        ("attempts", attempts),
        ("terminal_issues", terminal_issues),
        ("remaining_work", remaining_work),
    ):
        if parsed is None:
            issues.append(
                _issue("RECEIPT_FIELD_TYPE", f"{field} has an invalid typed structure")
            )
    if issues:
        return _error(*issues)

    receipt = ReconciliationExecutionReceipt(
        version=data["version"],
        kind=data["kind"],
        project_id=data["project_id"],
        requested_max_steps=data["requested_max_steps"],
        initial_state=data["initial_state"],
        git_head=data["git_head"],
        git_branch=data["git_branch"],
        policy_fingerprint=data["policy_fingerprint"],
        approval_digest=data["approval_digest"],
        approval_scope=data["approval_scope"],
        policy_decisions=policy_decisions or (),
        approval_verifications=approval_verifications or (),
        attempts=attempts or (),
        successful_steps=data["successful_steps"],
        terminal_state=data["terminal_state"],
        terminal_issues=tuple(sorted(terminal_issues or ())),
        final_plan_state=data["final_plan_state"],
        remaining_work=tuple(sorted(remaining_work or ())),
        digest=data["digest"],
    )
    expected = reconciliation_receipt_digest(receipt)
    if receipt.digest != expected:
        return _error(
            _issue("RECEIPT_DIGEST_INVALID", "receipt digest does not match payload")
        )
    return ReconciliationReceiptLoadResult(state="loaded", receipt=receipt, issues=())
