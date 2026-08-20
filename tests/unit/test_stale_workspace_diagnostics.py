from __future__ import annotations

import json
from pathlib import Path

from ai_engineering.opencode_control_protocol import (
    ControlResultState,
    ControlTaskClass,
    build_request,
)
from ai_engineering.opencode_readonly_adapter import (
    ReadOnlyOpenCodeAdapter,
    RepositorySnapshot,
)
from ai_engineering import opencode_worker_lifecycle as lifecycle


def make_snapshot(*, head: str, status: str = "") -> RepositorySnapshot:
    return RepositorySnapshot(
        branch="master",
        head=head,
        status=status,
        index_state_hash="1" * 64,
        worktree_diff_hash="2" * 64,
        cached_diff_hash="3" * 64,
        local_config_hash="4" * 64,
        remotes_hash="5" * 64,
    )


def test_stale_workspace_result_is_bounded_and_public_safe() -> None:
    expected = "a" * 40
    observed = "b" * 40
    request = build_request(
        task_class=ControlTaskClass.QUALITY_VERIFY,
        objective="Verify exact Quality.",
        repository="magixhot/AI-Engineering",
        expected_head=expected,
    )

    result = lifecycle.stale_workspace_result(
        request,
        make_snapshot(head=observed),
    )
    evidence = json.loads(result.text)

    assert result.state is ControlResultState.FAILED
    assert result.head == observed
    assert result.pre_clean is True
    assert result.post_clean is True
    assert evidence == {
        "expected_head": expected,
        "guidance": (
            "synchronize the local checkout to the expected commit with an "
            "operator-reviewed fast-forward; no automatic repository change "
            "was performed"
        ),
        "kind": "expected_head_mismatch",
        "observed_head": observed,
    }
    assert "/home/" not in result.text
    assert "C:\\" not in result.text


def test_configured_execution_fails_before_executor_on_stale_head(
    monkeypatch,
    tmp_path: Path,
) -> None:
    expected = "c" * 40
    observed = "d" * 40
    request = build_request(
        task_class=ControlTaskClass.QUALITY_VERIFY,
        objective="Verify exact Quality.",
        repository="magixhot/AI-Engineering",
        expected_head=expected,
    )
    snapshot = make_snapshot(head=observed)
    monkeypatch.setattr(lifecycle, "capture_repository_snapshot", lambda _: snapshot)

    def forbidden_quality(*args, **kwargs):
        raise AssertionError("quality verification must not run on stale workspace")

    monkeypatch.setattr(lifecycle, "execute_quality_verify", forbidden_quality)
    adapter = ReadOnlyOpenCodeAdapter(tmp_path)

    result = lifecycle.execute_configured_request(tmp_path, adapter, request)

    assert result.state is ControlResultState.FAILED
    assert result.head == observed
    assert json.loads(result.text)["kind"] == "expected_head_mismatch"


def test_stale_workspace_result_preserves_dirty_evidence() -> None:
    request = build_request(
        task_class=ControlTaskClass.STATUS,
        objective="Inspect status.",
        repository="magixhot/AI-Engineering",
        expected_head="e" * 40,
    )

    result = lifecycle.stale_workspace_result(
        request,
        make_snapshot(head="f" * 40, status=" M tracked.txt"),
    )

    assert result.state is ControlResultState.FAILED
    assert result.pre_clean is False
    assert result.post_clean is False
