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


def test_quality_verify_requires_exact_head() -> None:
    with pytest.raises(ControlProtocolError, match="requires expected_head"):
        build_request(
            task_class=ControlTaskClass.QUALITY_VERIFY,
            objective="verify exact post-merge Quality",
            repository="magixhot/AI-Engineering",
        )


def test_quality_verify_relay_succeeds_without_opencode(monkeypatch) -> None:
    request = build_request(
        task_class=ControlTaskClass.QUALITY_VERIFY,
        objective="verify exact post-merge Quality",
        repository="magixhot/AI-Engineering",
        expected_head=SHA,
    )

    def fake_verify(value):
        run = WorkflowRunEvidence(
            run_id=101,
            workflow_id=202,
            head_branch="master",
            head_sha=SHA,
            event="push",
            status="completed",
            conclusion="success",
            run_attempt=1,
        )
        return select_authoritative_run(value, [run])

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
