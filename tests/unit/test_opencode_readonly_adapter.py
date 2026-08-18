from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pytest

from ai_engineering.opencode_control_protocol import (
    ControlResultState,
    ControlTaskClass,
    build_request,
)
from ai_engineering.opencode_readonly_adapter import (
    READONLY_AGENT,
    OpenCodeAdapterError,
    OpenCodeHttpTransport,
    ReadOnlyOpenCodeAdapter,
    RepositorySnapshot,
)

REPOSITORY = "magixhot/AI-Engineering"
HEAD = "82fd8900e08ecad220cfe15e33de2b2bbc7268e9"


def snapshot(*, status: str = "", head: str = HEAD) -> RepositorySnapshot:
    return RepositorySnapshot(
        branch="master",
        head=head,
        status=status,
        index_state_hash="index",
        worktree_diff_hash="worktree",
        cached_diff_hash="cached",
        local_config_hash="config",
        remotes_hash="remotes",
    )


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Mapping[str, Any]]] = []

    def __call__(
        self,
        path: str,
        payload: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        self.calls.append((path, payload))
        if path == "/session":
            return {"id": "session-1"}
        return {
            "info": {"id": "message-1"},
            "parts": [{"type": "text", "text": "Repository is clean."}],
        }


def test_adapter_executes_with_named_readonly_agent_and_unchanged_state() -> None:
    states = iter([snapshot(), snapshot()])
    transport = FakeTransport()
    adapter = ReadOnlyOpenCodeAdapter(
        Path("."),
        transport=transport,
        snapshot_provider=lambda: next(states),
    )
    request = build_request(
        task_class=ControlTaskClass.STATUS,
        objective="Inspect repository status.",
        repository=REPOSITORY,
        expected_head=HEAD,
    )

    result = adapter.execute(request)

    assert result.state is ControlResultState.SUCCEEDED
    assert result.head == HEAD
    assert result.pre_clean is True
    assert result.post_clean is True
    assert result.text == "Repository is clean."
    assert transport.calls[0][0] == "/session"
    assert transport.calls[1][0] == "/session/session-1/message"
    assert transport.calls[1][1]["agent"] == READONLY_AGENT


def test_adapter_rejects_dirty_baseline_before_contacting_opencode() -> None:
    transport = FakeTransport()
    adapter = ReadOnlyOpenCodeAdapter(
        Path("."),
        transport=transport,
        snapshot_provider=lambda: snapshot(status="?? generated.txt"),
    )
    request = build_request(
        task_class=ControlTaskClass.INSPECT,
        objective="Inspect docs.",
        repository=REPOSITORY,
    )

    with pytest.raises(OpenCodeAdapterError, match="clean"):
        adapter.execute(request)

    assert transport.calls == []


def test_adapter_rejects_expected_head_mismatch() -> None:
    adapter = ReadOnlyOpenCodeAdapter(
        Path("."),
        transport=FakeTransport(),
        snapshot_provider=lambda: snapshot(head="0" * 40),
    )
    request = build_request(
        task_class=ControlTaskClass.STATUS,
        objective="Inspect status.",
        repository=REPOSITORY,
        expected_head=HEAD,
    )

    with pytest.raises(OpenCodeAdapterError, match="expected HEAD"):
        adapter.execute(request)


def test_adapter_fails_closed_when_repository_state_changes() -> None:
    states = iter(
        [
            snapshot(),
            RepositorySnapshot(
                branch="master",
                head=HEAD,
                status=" M README.md",
                index_state_hash="index",
                worktree_diff_hash="changed",
                cached_diff_hash="cached",
                local_config_hash="config",
                remotes_hash="remotes",
            ),
        ]
    )
    adapter = ReadOnlyOpenCodeAdapter(
        Path("."),
        transport=FakeTransport(),
        snapshot_provider=lambda: next(states),
    )
    request = build_request(
        task_class=ControlTaskClass.DIFF,
        objective="Inspect the current diff.",
        repository=REPOSITORY,
        expected_head=HEAD,
    )

    with pytest.raises(OpenCodeAdapterError, match="invariant changed"):
        adapter.execute(request)


def test_adapter_rejects_repository_identity_mismatch() -> None:
    adapter = ReadOnlyOpenCodeAdapter(
        Path("."),
        transport=FakeTransport(),
        snapshot_provider=snapshot,
    )
    request = build_request(
        task_class=ControlTaskClass.STATUS,
        objective="Inspect status.",
        repository="other/project",
    )

    with pytest.raises(OpenCodeAdapterError, match="identity mismatch"):
        adapter.execute(request)


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1:4096",
        "http://0.0.0.0:4096",
        "http://example.com:4096",
        "http://127.0.0.1",
        "http://127.0.0.1:4096/api",
    ],
)
def test_http_transport_rejects_non_loopback_or_ambiguous_urls(url: str) -> None:
    with pytest.raises(OpenCodeAdapterError):
        OpenCodeHttpTransport(url, directory=Path("."))


def test_adapter_bounds_result_to_request_limit() -> None:
    class LongTransport(FakeTransport):
        def __call__(
            self,
            path: str,
            payload: Mapping[str, Any],
        ) -> Mapping[str, Any]:
            if path == "/session":
                return {"id": "session-1"}
            return {"parts": [{"type": "text", "text": "x" * 300}]}

    states = iter([snapshot(), snapshot()])
    adapter = ReadOnlyOpenCodeAdapter(
        Path("."),
        transport=LongTransport(),
        snapshot_provider=lambda: next(states),
    )
    request = build_request(
        task_class=ControlTaskClass.PLAN,
        objective="Plan only.",
        repository=REPOSITORY,
        max_result_chars=256,
    )

    result = adapter.execute(request)

    assert len(result.text) == 256
