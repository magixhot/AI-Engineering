from __future__ import annotations

import json

import pytest

from ai_engineering.local_agent_routing import (
    LocalState,
    Route,
    RoutingRequest,
    TaskClass,
    decide_route,
    main,
)


@pytest.mark.parametrize(
    "task_class",
    [
        TaskClass.ARCHITECTURE,
        TaskClass.AUTHORITY,
        TaskClass.SECURITY,
        TaskClass.NONDETERMINISTIC_FAILURE,
    ],
)
def test_high_risk_classes_escalate_without_authorizing_codex(
    task_class: TaskClass,
) -> None:
    decision = decide_route(
        RoutingRequest(
            task_class=task_class,
            deterministic_verification=True,
        )
    )
    assert decision.route is Route.CODEX_ESCALATE
    assert decision.codex_execution_authorized is False
    assert decision.external_execution_authorized is False


def test_bounded_deterministic_task_routes_local() -> None:
    decision = decide_route(
        RoutingRequest(
            task_class=TaskClass.BOUNDED_IMPLEMENTATION,
            deterministic_verification=True,
        )
    )
    assert decision.route is Route.LOCAL
    assert decision.local_first is True


def test_write_task_without_deterministic_verification_escalates() -> None:
    decision = decide_route(
        RoutingRequest(
            task_class=TaskClass.MECHANICAL_EDIT,
            deterministic_verification=False,
        )
    )
    assert decision.route is Route.CODEX_ESCALATE
    assert decision.codex_execution_authorized is False


def test_local_escalate_goes_directly_to_codex_handoff() -> None:
    decision = decide_route(
        RoutingRequest(
            task_class=TaskClass.INSPECTION,
            deterministic_verification=True,
            local_state=LocalState.ESCALATE,
            external_fallback_approved=True,
            external_model="opencode/mimo-v2.5-free",
        )
    )
    assert decision.route is Route.CODEX_ESCALATE
    assert decision.external_execution_authorized is False


def test_local_failure_does_not_replay_without_explicit_fallback() -> None:
    decision = decide_route(
        RoutingRequest(
            task_class=TaskClass.VERIFICATION,
            deterministic_verification=True,
            local_state=LocalState.FAIL,
        )
    )
    assert decision.route is Route.BLOCKED
    assert decision.external_execution_authorized is False


def test_external_fallback_requires_approval_and_exact_model() -> None:
    no_model = decide_route(
        RoutingRequest(
            task_class=TaskClass.INSPECTION,
            deterministic_verification=True,
            local_state=LocalState.BLOCKED,
            external_fallback_approved=True,
        )
    )
    assert no_model.route is Route.BLOCKED

    approved = decide_route(
        RoutingRequest(
            task_class=TaskClass.INSPECTION,
            deterministic_verification=True,
            local_state=LocalState.BLOCKED,
            external_fallback_approved=True,
            external_model="opencode/mimo-v2.5-free",
        )
    )
    assert approved.route is Route.EXTERNAL_EXPLICIT
    assert approved.external_execution_authorized is True
    assert approved.codex_execution_authorized is False


def test_local_unavailable_fails_closed_without_fallback() -> None:
    decision = decide_route(
        RoutingRequest(
            task_class=TaskClass.INSPECTION,
            deterministic_verification=True,
            local_available=False,
        )
    )
    assert decision.route is Route.BLOCKED


def test_local_pass_never_routes_to_cloud() -> None:
    decision = decide_route(
        RoutingRequest(
            task_class=TaskClass.VERIFICATION,
            deterministic_verification=True,
            local_state=LocalState.PASS,
            external_fallback_approved=True,
            external_model="opencode/mimo-v2.5-free",
        )
    )
    assert decision.route is Route.LOCAL
    assert decision.external_execution_authorized is False
    assert decision.codex_execution_authorized is False


def test_cli_emits_stable_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(
        [
            "--task-class",
            "inspection",
            "--deterministic-verification",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["decision"]["route"] == "LOCAL"
    assert payload["request"]["task_class"] == "inspection"
    assert payload["request"]["local_state"] == "not_attempted"
