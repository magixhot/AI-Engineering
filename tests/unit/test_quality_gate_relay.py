from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_engineering import quality_gate_relay
from ai_engineering.opencode_control_protocol import (
    ControlProtocolError,
    ControlResultState,
    ControlTaskClass,
    build_request,
)
from ai_engineering.opencode_readonly_adapter import RepositorySnapshot
from ai_engineering.quality_verification import WorkflowRunEvidence
from ai_engineering.quality_verifier import select_authoritative_run

SHA = "0123456789abcdef0123456789abcdef01234567"


def _snapshot() -> RepositorySnapshot:
    return RepositorySnapshot(
        branch="master",
        head=SHA,
        status="",
        index_state_hash="a",
        worktree_diff_hash="b",
        cached_diff_hash="c",
        local_config_hash="d",
        remotes_hash="e",
    )


def _run(*, status: str, conclusion: str | None) -> WorkflowRunEvidence:
    return WorkflowRunEvidence(
        run_id=101,
        workflow_id=202,
        head_branch="master",
        head_sha=SHA,
        event="push",
        status=status,
        conclusion=conclusion,
        run_attempt=1,
    )


def _request():
    return build_request(
        task_class=ControlTaskClass.QUALITY_VERIFY,
        objective="verify exact post-merge Quality",
        repository="magixhot/AI-Engineering",
        expected_head=SHA,
    )


def test_quality_verify_requires_exact_head() -> None:
    with pytest.raises(ControlProtocolError, match="requires expected_head"):
        build_request(
            task_class=ControlTaskClass.QUALITY_VERIFY,
            objective="verify exact post-merge Quality",
            repository="magixhot/AI-Engineering",
        )


def test_quality_verify_relay_succeeds_without_opencode(monkeypatch) -> None:
    request = _request()

    def fake_verify(value):
        return select_authoritative_run(
            value,
            [_run(status="completed", conclusion="success")],
        )

    monkeypatch.setattr(
        quality_gate_relay,
        "verify_exact_post_merge_quality",
        fake_verify,
    )
    result = quality_gate_relay.execute_quality_verify(
        Path("/unused"),
        request,
        snapshot_provider=_snapshot,
    )

    assert result.state is ControlResultState.SUCCEEDED
    assert result.head == SHA
    assert result.pre_clean is True
    assert result.post_clean is True
    document = json.loads(result.text)
    assert document["satisfies_gate"] is True
    assert document["head_sha"] == SHA
    assert document["evidence"]["run_id"] == 101


def test_quality_verify_relay_waits_for_pending_run(monkeypatch) -> None:
    request = _request()
    runs = iter(
        [
            _run(status="in_progress", conclusion=None),
            _run(status="completed", conclusion="success"),
        ]
    )
    sleeps: list[float] = []

    def fake_verify(value):
        return select_authoritative_run(value, [next(runs)])

    monkeypatch.setattr(
        quality_gate_relay,
        "verify_exact_post_merge_quality",
        fake_verify,
    )
    monkeypatch.setattr(quality_gate_relay.time, "sleep", sleeps.append)

    result = quality_gate_relay.execute_quality_verify(
        Path("/unused"),
        request,
        snapshot_provider=_snapshot,
    )

    assert result.state is ControlResultState.SUCCEEDED
    assert sleeps == [quality_gate_relay.QUALITY_RELAY_POLL_SECONDS]
    document = json.loads(result.text)
    assert document["state"] == "SUCCEEDED"
    assert document["evidence"]["status"] == "completed"


def test_quality_verify_relay_bounds_pending_timeout(monkeypatch) -> None:
    request = _request()
    monkeypatch.setattr(quality_gate_relay, "QUALITY_RELAY_MAX_ATTEMPTS", 2)
    monkeypatch.setattr(quality_gate_relay.time, "sleep", lambda _: None)

    def fake_verify(value):
        return select_authoritative_run(
            value,
            [_run(status="queued", conclusion=None)],
        )

    monkeypatch.setattr(
        quality_gate_relay,
        "verify_exact_post_merge_quality",
        fake_verify,
    )
    result = quality_gate_relay.execute_quality_verify(
        Path("/unused"),
        request,
        snapshot_provider=_snapshot,
    )

    assert result.state is ControlResultState.FAILED
    document = json.loads(result.text)
    assert document["state"] == "UNAVAILABLE"
    assert document["reason"] == (
        "terminal Quality state not observed before relay timeout"
    )
