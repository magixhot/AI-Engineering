from __future__ import annotations

import json

import pytest

import ai_engineering.opencode_control_worker as worker_module
from ai_engineering.opencode_control_worker import (
    ControlWorkerError,
    GhIssueTransport,
)


def test_control_issue_transport_consumes_all_pages(monkeypatch) -> None:
    transport = GhIssueTransport(repository="owner/repo", issue_number=7)
    calls: list[tuple[str, ...]] = []
    pages = [
        [
            {
                "id": comment_id,
                "user": {"login": "magixhot"},
                "body": f"comment-{comment_id}",
            }
            for comment_id in range(1, 101)
        ],
        [{"id": 101, "user": {"login": "magixhot"}, "body": "last"}],
    ]

    def fake_run(*args: str) -> str:
        calls.append(args)
        return json.dumps(pages[len(calls) - 1])

    monkeypatch.setattr(transport, "_run", fake_run)
    comments = transport.list_comments()

    assert [comment.comment_id for comment in comments] == list(range(1, 102))
    assert calls == [
        (
            "api",
            "repos/owner/repo/issues/7/comments?per_page=100&page=1",
        ),
        (
            "api",
            "repos/owner/repo/issues/7/comments?per_page=100&page=2",
        ),
    ]


def test_control_issue_transport_fails_closed_at_page_bound(monkeypatch) -> None:
    monkeypatch.setattr(worker_module, "MAX_CONTROL_COMMENT_PAGES", 2)
    transport = GhIssueTransport(repository="owner/repo", issue_number=7)
    full_page = [
        {"id": item, "user": {"login": "magixhot"}, "body": "comment"}
        for item in range(100)
    ]
    calls = 0

    def fake_run(*_args: str) -> str:
        nonlocal calls
        calls += 1
        return json.dumps(full_page)

    monkeypatch.setattr(transport, "_run", fake_run)

    with pytest.raises(ControlWorkerError, match="pagination limit"):
        transport.list_comments()

    assert calls == 6
