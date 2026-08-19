from __future__ import annotations

import json

import pytest

from ai_engineering.quality_actions_transport import (
    GhActionsReadTransport,
    QualityActionsTransportError,
)
from ai_engineering.quality_verification import build_verification_input

SHA = "0123456789abcdef0123456789abcdef01234567"


def _run(run_id: int, **overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "id": run_id,
        "workflow_id": 456,
        "head_branch": "master",
        "head_sha": SHA,
        "event": "push",
        "status": "completed",
        "conclusion": "success",
        "run_attempt": 1,
    }
    value.update(overrides)
    return value


def _input():
    return build_verification_input(
        repository="magixhot/AI-Engineering",
        head_sha=SHA,
    )


def test_transport_uses_exact_read_only_paginated_query() -> None:
    commands: list[tuple[str, ...]] = []

    def runner(command: tuple[str, ...]) -> str:
        commands.append(command)
        return json.dumps([{"workflow_runs": []}])

    result = GhActionsReadTransport(runner=runner).list_runs(_input())

    assert result == []
    assert len(commands) == 1
    command = commands[0]
    assert command[:4] == ("gh", "api", "--paginate", "--slurp")
    endpoint = command[4]
    assert endpoint.startswith(
        "repos/magixhot/AI-Engineering/actions/workflows/quality.yml/runs?"
    )
    assert "branch=master" in endpoint
    assert "event=push" in endpoint
    assert f"head_sha={SHA}" in endpoint
    assert "per_page=100" in endpoint
    assert "--method" not in command


def test_transport_collects_every_slurped_page() -> None:
    payload = [
        {"workflow_runs": [_run(1)]},
        {"workflow_runs": [_run(2, conclusion="failure")]},
    ]

    transport = GhActionsReadTransport(runner=lambda _command: json.dumps(payload))
    evidence = transport.list_runs(_input())

    assert [item.run_id for item in evidence] == [1, 2]
    assert evidence[0].conclusion == "success"
    assert evidence[1].conclusion == "failure"


@pytest.mark.parametrize(
    "raw",
    [
        "not-json",
        json.dumps({"workflow_runs": []}),
        json.dumps([[]]),
        json.dumps([{}]),
        json.dumps([{"workflow_runs": {}}]),
        json.dumps([{"workflow_runs": ["bad"]}]),
    ],
)
def test_transport_fails_closed_on_malformed_pages(raw: str) -> None:
    transport = GhActionsReadTransport(runner=lambda _command: raw)

    with pytest.raises(QualityActionsTransportError):
        transport.list_runs(_input())


def test_transport_fails_closed_on_malformed_run_evidence() -> None:
    raw = json.dumps([{"workflow_runs": [_run(1, head_sha="short")]}])
    transport = GhActionsReadTransport(runner=lambda _command: raw)

    with pytest.raises(QualityActionsTransportError):
        transport.list_runs(_input())


def test_transport_propagates_only_bounded_transport_error() -> None:
    def runner(_command: tuple[str, ...]) -> str:
        raise QualityActionsTransportError("GitHub Actions read failed")

    transport = GhActionsReadTransport(runner=runner)

    with pytest.raises(
        QualityActionsTransportError,
        match="GitHub Actions read failed",
    ):
        transport.list_runs(_input())
