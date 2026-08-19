from __future__ import annotations

import json

from ai_engineering.opencode_control_worker import GhIssueTransport


def test_control_issue_transport_consumes_all_pages(monkeypatch) -> None:
    transport = GhIssueTransport(repository="owner/repo", issue_number=7)
    calls: list[tuple[str, ...]] = []
    pages = [
        [{"id": 1, "user": {"login": "magixhot"}, "body": "first"}],
        [{"id": 2, "user": {"login": "magixhot"}, "body": "second"}],
    ]

    def fake_run(*args: str) -> str:
        calls.append(args)
        return json.dumps(pages)

    monkeypatch.setattr(transport, "_run", fake_run)
    comments = transport.list_comments()

    assert [comment.comment_id for comment in comments] == [1, 2]
    assert calls == [
        (
            "api",
            "--paginate",
            "--slurp",
            "repos/owner/repo/issues/7/comments?per_page=100",
        )
    ]
