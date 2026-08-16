import json

from ai_engineering.project_reconciliation_approval import (
    build_reconciliation_approval,
    parse_reconciliation_approval,
    serialize_reconciliation_approval,
)


def _approval():
    return build_reconciliation_approval(
        project_id="project-v1:example",
        workflow="NEXT_DOCS_PLAN",
        candidate_inputs=(("z", "last"), ("a", "first")),
        git_head="0123456789abcdef",
        git_branch="main",
        policy_fingerprint="policy-sha256:abc",
    )


def test_build_is_deterministic_across_candidate_input_order() -> None:
    left = _approval()
    right = build_reconciliation_approval(
        project_id="project-v1:example",
        workflow="NEXT_DOCS_PLAN",
        candidate_inputs=(("a", "first"), ("z", "last")),
        git_head="0123456789abcdef",
        git_branch="main",
        policy_fingerprint="policy-sha256:abc",
    )

    assert left == right
    assert len(left.digest) == 64


def test_serialization_is_canonical_and_round_trips() -> None:
    approval = _approval()
    encoded = serialize_reconciliation_approval(approval)

    assert encoded.endswith(b"\n")
    assert b" " not in encoded
    loaded = parse_reconciliation_approval(encoded)
    assert loaded.state == "loaded"
    assert loaded.approval == approval
    assert loaded.issues == ()


def test_authority_relevant_drift_changes_digest() -> None:
    baseline = _approval()
    changed = build_reconciliation_approval(
        project_id=baseline.project_id,
        workflow="NEXT_OWNERSHIP_PLAN",
        candidate_inputs=baseline.candidate_inputs,
        git_head=baseline.git_head,
        git_branch=baseline.git_branch,
        policy_fingerprint=baseline.policy_fingerprint,
    )

    assert changed.digest != baseline.digest


def test_tampered_payload_fails_closed() -> None:
    data = json.loads(serialize_reconciliation_approval(_approval()))
    data["git_head"] = "different"

    loaded = parse_reconciliation_approval(json.dumps(data).encode())

    assert loaded.state == "approval_error"
    assert loaded.approval is None
    assert [issue.code for issue in loaded.issues] == ["APPROVAL_DIGEST_INVALID"]


def test_unknown_field_fails_closed_before_digest_use() -> None:
    data = json.loads(serialize_reconciliation_approval(_approval()))
    data["surprise"] = True

    loaded = parse_reconciliation_approval(json.dumps(data).encode())

    assert loaded.state == "approval_error"
    assert loaded.approval is None
    assert [issue.code for issue in loaded.issues] == ["APPROVAL_UNKNOWN_FIELD"]


def test_unsupported_version_fails_closed() -> None:
    data = json.loads(serialize_reconciliation_approval(_approval()))
    data["version"] = 2

    loaded = parse_reconciliation_approval(json.dumps(data).encode())

    assert loaded.state == "approval_error"
    assert loaded.approval is None
    assert [issue.code for issue in loaded.issues] == ["APPROVAL_VERSION_UNSUPPORTED"]


def test_non_object_and_malformed_json_fail_closed() -> None:
    non_object = parse_reconciliation_approval(b"[]")
    malformed = parse_reconciliation_approval(b"{")

    assert [issue.code for issue in non_object.issues] == ["APPROVAL_ROOT_TYPE"]
    assert [issue.code for issue in malformed.issues] == ["APPROVAL_PARSE_ERROR"]


def test_scope_other_than_single_candidate_fails_closed() -> None:
    data = json.loads(serialize_reconciliation_approval(_approval()))
    data["scope"] = "whole_run"

    loaded = parse_reconciliation_approval(json.dumps(data).encode())

    assert loaded.state == "approval_error"
    assert loaded.approval is None
    assert [issue.code for issue in loaded.issues] == ["APPROVAL_SCOPE_INVALID"]
