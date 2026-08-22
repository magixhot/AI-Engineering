from __future__ import annotations

import json
from pathlib import Path

from ai_engineering.local_agent_routing import Route
from ai_engineering.local_agent_shadow import (
    CASES,
    LOCAL_MODEL,
    ShadowObservation,
    expected_routes,
    main,
    validate_observations,
)


def _passing_observations() -> list[ShadowObservation]:
    return [
        ShadowObservation(
            case_id=case.case_id,
            model=LOCAL_MODEL,
            role=case.role,
            terminal_state="PASS",
            repository_clean_before=True,
            repository_clean_after=True,
            head_unchanged=True,
            deterministic_check_passed=True,
        )
        for case in CASES
    ]


def test_representative_cases_route_local() -> None:
    assert expected_routes() == {case.case_id: Route.LOCAL for case in CASES}


def test_complete_passing_observations_validate() -> None:
    valid, issues = validate_observations(_passing_observations())
    assert valid is True
    assert issues == ()


def test_missing_case_fails_closed() -> None:
    valid, issues = validate_observations(_passing_observations()[:-1])
    assert valid is False
    assert issues == (f"missing case: {CASES[-1].case_id}",)


def test_wrong_model_fails_closed() -> None:
    observations = _passing_observations()
    first = observations[0]
    observations[0] = ShadowObservation(
        case_id=first.case_id,
        model="opencode/mimo-v2.5-free",
        role=first.role,
        terminal_state=first.terminal_state,
        repository_clean_before=first.repository_clean_before,
        repository_clean_after=first.repository_clean_after,
        head_unchanged=first.head_unchanged,
        deterministic_check_passed=first.deterministic_check_passed,
    )
    valid, issues = validate_observations(observations)
    assert valid is False
    assert issues == (f"unexpected model: {first.case_id}",)


def test_mutation_or_failed_check_fails_closed() -> None:
    observations = _passing_observations()
    first = observations[0]
    observations[0] = ShadowObservation(
        case_id=first.case_id,
        model=first.model,
        role=first.role,
        terminal_state=first.terminal_state,
        repository_clean_before=True,
        repository_clean_after=False,
        head_unchanged=False,
        deterministic_check_passed=False,
    )
    valid, issues = validate_observations(observations)
    assert valid is False
    assert f"dirty after: {first.case_id}" in issues
    assert f"HEAD changed: {first.case_id}" in issues
    assert f"deterministic check failed: {first.case_id}" in issues


def test_cli_lists_cases(capsys) -> None:
    assert main(["--list-cases"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert [item["case_id"] for item in payload] == [case.case_id for case in CASES]
    assert all(item["expected_route"] == "LOCAL" for item in payload)


def test_cli_validates_evidence(tmp_path: Path, capsys) -> None:
    path = tmp_path / "evidence.json"
    path.write_text(
        json.dumps(
            [
                {
                    "case_id": observation.case_id,
                    "model": observation.model,
                    "role": observation.role,
                    "terminal_state": observation.terminal_state,
                    "repository_clean_before": observation.repository_clean_before,
                    "repository_clean_after": observation.repository_clean_after,
                    "head_unchanged": observation.head_unchanged,
                    "deterministic_check_passed": observation.deterministic_check_passed,
                }
                for observation in _passing_observations()
            ]
        ),
        encoding="utf-8",
    )
    assert main(["--evidence", str(path)]) == 0
    assert json.loads(capsys.readouterr().out) == {"issues": [], "valid": True}
