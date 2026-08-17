from __future__ import annotations

import json

from ai_engineering.project_reconciliation_receipt import (
    ReceiptApplyAttempt,
    ReceiptApprovalVerification,
    ReceiptPolicyDecision,
    build_reconciliation_execution_receipt,
    parse_reconciliation_execution_receipt,
    serialize_reconciliation_execution_receipt,
)


def _receipt(**overrides: object):
    values: dict[str, object] = {
        "project_id": "project:demo",
        "requested_max_steps": 8,
        "initial_state": "ready",
        "git_head": "abc123",
        "git_branch": "main",
        "policy_fingerprint": "policy-sha256",
        "approval_digest": "approval-sha256",
        "approval_scope": "single_candidate",
        "policy_decisions": (
            ReceiptPolicyDecision(
                workflow="documentation_sync",
                state="allowed",
                effective_max_steps=2,
                issues=(("Z", "last"), ("A", "first")),
            ),
        ),
        "approval_verifications": (
            ReceiptApprovalVerification(
                workflow="documentation_sync",
                state="approved",
                issues=(),
            ),
        ),
        "attempts": (
            ReceiptApplyAttempt(
                sequence=1,
                workflow="documentation_sync",
                state="applied",
                write_attempted=True,
                delegated_subsystem="AUTO-0002",
                rollback_status="not_applicable",
                post_apply_state="healthy",
                issues=(("B", "second"), ("A", "first")),
            ),
        ),
        "successful_steps": 1,
        "terminal_state": "complete",
        "terminal_issues": (("Z", "last"), ("A", "first")),
        "final_plan_state": "clean",
        "remaining_work": (),
    }
    values.update(overrides)
    return build_reconciliation_execution_receipt(**values)  # type: ignore[arg-type]


def test_equivalent_set_like_evidence_has_identical_bytes_and_digest() -> None:
    first = _receipt(
        terminal_issues=(("Z", "last"), ("A", "first")),
    )
    second = _receipt(
        terminal_issues=(("A", "first"), ("Z", "last")),
    )

    assert first.digest == second.digest
    assert serialize_reconciliation_execution_receipt(first) == (
        serialize_reconciliation_execution_receipt(second)
    )


def test_execution_order_remains_digest_relevant() -> None:
    first = _receipt(
        attempts=(
            ReceiptApplyAttempt(
                sequence=1,
                workflow="documentation_sync",
                state="applied",
                write_attempted=True,
                delegated_subsystem="AUTO-0002",
                rollback_status="not_applicable",
                post_apply_state="ready",
            ),
            ReceiptApplyAttempt(
                sequence=1,
                workflow="project_migration",
                state="applied",
                write_attempted=True,
                delegated_subsystem="AUTO-0004/AUTO-0005",
                rollback_status="not_applicable",
                post_apply_state="healthy",
            ),
        ),
        successful_steps=2,
    )
    second = _receipt(
        attempts=tuple(reversed(first.attempts)),
        successful_steps=2,
    )

    assert first.digest != second.digest


def test_authority_relevant_change_changes_digest() -> None:
    baseline = _receipt()
    changed = _receipt(git_head="different")

    assert baseline.digest != changed.digest


def test_round_trip_is_strict_and_deterministic() -> None:
    receipt = _receipt()
    raw = serialize_reconciliation_execution_receipt(receipt)
    loaded = parse_reconciliation_execution_receipt(raw)

    assert loaded.state == "loaded"
    assert loaded.issues == ()
    assert loaded.receipt == receipt
    assert loaded.receipt is not None
    assert serialize_reconciliation_execution_receipt(loaded.receipt) == raw
    assert raw.endswith(b"\n")


def test_unknown_and_missing_fields_fail_closed() -> None:
    data = json.loads(serialize_reconciliation_execution_receipt(_receipt()))
    data["unexpected"] = "value"
    del data["kind"]

    loaded = parse_reconciliation_execution_receipt(
        json.dumps(data, separators=(",", ":")).encode()
    )

    assert loaded.state == "receipt_error"
    assert loaded.receipt is None
    assert [issue.code for issue in loaded.issues] == [
        "RECEIPT_MISSING_FIELD",
        "RECEIPT_UNKNOWN_FIELD",
    ]


def test_unsupported_version_fails_closed() -> None:
    data = json.loads(serialize_reconciliation_execution_receipt(_receipt()))
    data["version"] = 2

    loaded = parse_reconciliation_execution_receipt(json.dumps(data).encode())

    assert loaded.state == "receipt_error"
    assert any(issue.code == "RECEIPT_VERSION_UNSUPPORTED" for issue in loaded.issues)


def test_digest_mismatch_fails_closed() -> None:
    data = json.loads(serialize_reconciliation_execution_receipt(_receipt()))
    data["terminal_state"] = "failed"

    loaded = parse_reconciliation_execution_receipt(json.dumps(data).encode())

    assert loaded.state == "receipt_error"
    assert loaded.receipt is None
    assert loaded.issues[0].code == "RECEIPT_DIGEST_INVALID"


def test_invalid_nested_structure_fails_closed() -> None:
    data = json.loads(serialize_reconciliation_execution_receipt(_receipt()))
    data["attempts"][0]["write_attempted"] = "yes"

    loaded = parse_reconciliation_execution_receipt(json.dumps(data).encode())

    assert loaded.state == "receipt_error"
    assert any(
        issue.code == "RECEIPT_FIELD_TYPE" and "attempts" in issue.detail
        for issue in loaded.issues
    )


def test_parser_rejects_non_object_root_and_malformed_json() -> None:
    non_object = parse_reconciliation_execution_receipt(b"[]")
    malformed = parse_reconciliation_execution_receipt(b"{")

    assert non_object.state == "receipt_error"
    assert non_object.issues[0].code == "RECEIPT_ROOT_TYPE"
    assert malformed.state == "receipt_error"
    assert malformed.issues[0].code == "RECEIPT_PARSE_ERROR"


def test_serialized_receipt_has_no_volatile_fields() -> None:
    data = json.loads(serialize_reconciliation_execution_receipt(_receipt()))

    assert "timestamp" not in data
    assert "hostname" not in data
    assert "pid" not in data
    assert "project_path" not in data
