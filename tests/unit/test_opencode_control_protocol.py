from __future__ import annotations

import json

import pytest

from ai_engineering.opencode_control_protocol import (
    ControlProtocolError,
    ControlRequest,
    ControlResult,
    ControlResultState,
    ControlTaskClass,
    build_request,
    derive_request_id,
    parse_request,
    parse_result,
    serialize_request,
    serialize_result,
    validate_result_for_request,
)

REPOSITORY = "magixhot/AI-Engineering"
HEAD = "8461b5f309050cb831e599d2acc33b18bd421d34"


def test_request_round_trip_is_canonical_and_deterministic() -> None:
    request = build_request(
        task_class=ControlTaskClass.INSPECT,
        objective="Inspect the authoritative project documentation.",
        repository=REPOSITORY,
        expected_head=HEAD,
        max_result_chars=4_000,
    )

    encoded = serialize_request(request)
    reparsed = parse_request(encoded)

    assert reparsed == request
    assert serialize_request(reparsed) == encoded
    assert request.request_id == derive_request_id(
        task_class=ControlTaskClass.INSPECT,
        objective="Inspect the authoritative project documentation.",
        repository=REPOSITORY,
        expected_head=HEAD,
        max_result_chars=4_000,
    )
    assert encoded == json.dumps(
        json.loads(encoded),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def test_request_id_changes_when_authority_relevant_payload_changes() -> None:
    first = build_request(
        task_class=ControlTaskClass.STATUS,
        objective="Inspect repository status.",
        repository=REPOSITORY,
        expected_head=HEAD,
    )
    second = build_request(
        task_class=ControlTaskClass.DIFF,
        objective="Inspect repository status.",
        repository=REPOSITORY,
        expected_head=HEAD,
    )

    assert first.request_id != second.request_id


@pytest.mark.parametrize("task_class", ["test", "shell", "edit", "commit", "push"])
def test_request_rejects_unknown_or_write_capable_task_classes(task_class: str) -> None:
    request = build_request(
        task_class=ControlTaskClass.STATUS,
        objective="Inspect status.",
        repository=REPOSITORY,
    )
    value = json.loads(serialize_request(request))
    value["task_class"] = task_class

    with pytest.raises(ControlProtocolError, match="unknown task class"):
        parse_request(json.dumps(value))


def test_request_rejects_unknown_fields() -> None:
    request = build_request(
        task_class=ControlTaskClass.PLAN,
        objective="Plan the next bounded engineering step.",
        repository=REPOSITORY,
    )
    value = json.loads(serialize_request(request))
    value["shell"] = "git status"

    with pytest.raises(ControlProtocolError, match="fields"):
        parse_request(json.dumps(value))


def test_request_rejects_tampered_payload_with_existing_id() -> None:
    request = build_request(
        task_class=ControlTaskClass.INSPECT,
        objective="Inspect docs.",
        repository=REPOSITORY,
    )
    value = json.loads(serialize_request(request))
    value["objective"] = "Inspect docs and edit them."

    with pytest.raises(ControlProtocolError, match="request_id does not match"):
        parse_request(json.dumps(value))


def test_request_rejects_invalid_head_and_bounds() -> None:
    with pytest.raises(ControlProtocolError, match="expected_head"):
        build_request(
            task_class=ControlTaskClass.STATUS,
            objective="Inspect status.",
            repository=REPOSITORY,
            expected_head="8461b5f",
        )

    with pytest.raises(ControlProtocolError, match="max_result_chars"):
        build_request(
            task_class=ControlTaskClass.STATUS,
            objective="Inspect status.",
            repository=REPOSITORY,
            max_result_chars=100,
        )


def test_result_round_trip_and_request_scope_validation() -> None:
    request = build_request(
        task_class=ControlTaskClass.STATUS,
        objective="Inspect status.",
        repository=REPOSITORY,
        expected_head=HEAD,
        max_result_chars=1_000,
    )
    result = ControlResult(
        request_id=request.request_id,
        task_class=request.task_class,
        repository=request.repository,
        branch="master",
        head=HEAD,
        pre_clean=True,
        state=ControlResultState.SUCCEEDED,
        text="Branch master is clean and aligned with origin/master.",
        post_clean=True,
    )

    encoded = serialize_result(result)

    assert parse_result(encoded) == result
    validate_result_for_request(result, request)


def test_result_validation_fails_closed_on_scope_mismatch() -> None:
    request = build_request(
        task_class=ControlTaskClass.STATUS,
        objective="Inspect status.",
        repository=REPOSITORY,
        expected_head=HEAD,
    )
    result = ControlResult(
        request_id=request.request_id,
        task_class=ControlTaskClass.DIFF,
        repository=request.repository,
        branch="master",
        head=HEAD,
        pre_clean=True,
        state=ControlResultState.SUCCEEDED,
        text="No diff.",
        post_clean=True,
    )

    with pytest.raises(ControlProtocolError, match="task class"):
        validate_result_for_request(result, request)


def test_result_validation_enforces_request_text_bound() -> None:
    request = build_request(
        task_class=ControlTaskClass.INSPECT,
        objective="Inspect docs.",
        repository=REPOSITORY,
        max_result_chars=256,
    )
    result = ControlResult(
        request_id=request.request_id,
        task_class=request.task_class,
        repository=request.repository,
        branch="master",
        head=HEAD,
        pre_clean=True,
        state=ControlResultState.SUCCEEDED,
        text="x" * 257,
        post_clean=True,
    )

    with pytest.raises(ControlProtocolError, match="request bound"):
        validate_result_for_request(result, request)


def test_serialize_request_rejects_forged_request_id() -> None:
    request = ControlRequest(
        request_id="sha256:" + "0" * 64,
        task_class=ControlTaskClass.STATUS,
        objective="Inspect status.",
        repository=REPOSITORY,
    )

    with pytest.raises(ControlProtocolError, match="request_id does not match"):
        serialize_request(request)
