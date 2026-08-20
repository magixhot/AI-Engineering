from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from ai_engineering.opencode_control_protocol import (
    ControlRequest,
    ControlResult,
    ControlResultState,
    ControlTaskClass,
    build_request,
)
from ai_engineering.opencode_control_worker import (
    RECOVERY_FENCE,
    GitHubControlWorker,
    IssueComment,
    format_claim_comment,
    format_request_comment,
    format_result_comment,
)

REPOSITORY = "magixhot/AI-Engineering"
HEAD = "fb4524adf29e91bc0249a55d451ddd616014ccf3"
BASE_TIME = datetime(2026, 8, 20, 16, 0, tzinfo=timezone.utc)


class SequencedTransport:
    def __init__(self, batches: Iterable[Iterable[IssueComment]]) -> None:
        self._batches = [list(batch) for batch in batches]
        self.posted: list[str] = []
        self.reads = 0

    def list_comments(self) -> list[IssueComment]:
        index = min(self.reads, len(self._batches) - 1)
        self.reads += 1
        return list(self._batches[index])

    def post_comment(self, body: str) -> None:
        self.posted.append(body)


def make_request() -> ControlRequest:
    return build_request(
        task_class=ControlTaskClass.STATUS,
        objective="Inspect repository status.",
        repository=REPOSITORY,
        expected_head=HEAD,
        max_result_chars=1000,
    )


def make_result(request: ControlRequest) -> ControlResult:
    return ControlResult(
        request_id=request.request_id,
        task_class=request.task_class,
        repository=request.repository,
        branch="master",
        head=HEAD,
        pre_clean=True,
        state=ControlResultState.SUCCEEDED,
        text="Repository is clean.",
        post_clean=True,
    )


def never_execute(request: ControlRequest) -> ControlResult:
    raise AssertionError(f"recovery must not execute {request.request_id}")


def claim_fixture(
    *, claim_age_seconds: int
) -> tuple[ControlRequest, list[IssueComment]]:
    request = make_request()
    claim_time = BASE_TIME - timedelta(seconds=claim_age_seconds)
    comments = [
        IssueComment(
            10,
            "magixhot",
            format_request_comment(request),
            claim_time - timedelta(seconds=1),
        ),
        IssueComment(
            11,
            "magixhot",
            format_claim_comment(request.request_id),
            claim_time,
        ),
    ]
    return request, comments


def test_aged_claim_is_terminalized_without_replay() -> None:
    request, comments = claim_fixture(claim_age_seconds=301)
    transport = SequencedTransport([comments, comments])
    worker = GitHubControlWorker(
        transport=transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )

    assert worker.poll_once() == request.request_id
    assert transport.reads == 2
    assert len(transport.posted) == 1
    assert transport.posted[0].startswith(f"```{RECOVERY_FENCE}\n")
    assert '"state":"FAILED"' in transport.posted[0]
    assert '"reason":"claimed_without_terminal_result"' in transport.posted[0]
    assert '"replay_attempted":false' in transport.posted[0]


def test_fresh_claim_inside_grace_interval_is_not_terminalized() -> None:
    _, comments = claim_fixture(claim_age_seconds=299)
    transport = SequencedTransport([comments])
    worker = GitHubControlWorker(
        transport=transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )

    assert worker.poll_once() is None
    assert transport.reads == 1
    assert transport.posted == []


def test_visible_terminal_result_suppresses_recovery() -> None:
    request, comments = claim_fixture(claim_age_seconds=301)
    comments.append(
        IssueComment(
            12,
            "magixhot",
            format_result_comment(make_result(request)),
            BASE_TIME - timedelta(seconds=100),
        )
    )
    transport = SequencedTransport([comments])
    worker = GitHubControlWorker(
        transport=transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )

    assert worker.poll_once() is None
    assert transport.reads == 1
    assert transport.posted == []


def test_reinspection_detects_terminal_result_race() -> None:
    request, initial = claim_fixture(claim_age_seconds=301)
    reinspected = [
        *initial,
        IssueComment(
            12,
            "magixhot",
            format_result_comment(make_result(request)),
            BASE_TIME,
        ),
    ]
    transport = SequencedTransport([initial, reinspected])
    worker = GitHubControlWorker(
        transport=transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )

    assert worker.poll_once() is None
    assert transport.reads == 2
    assert transport.posted == []


def test_malformed_originating_request_is_never_recovered_or_executed() -> None:
    request, comments = claim_fixture(claim_age_seconds=301)
    comments[0] = IssueComment(
        10,
        "magixhot",
        "```auto-0013-request\nnot json\n```",
        comments[0].created_at,
    )
    transport = SequencedTransport([comments])
    worker = GitHubControlWorker(
        transport=transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )

    assert worker.poll_once() is None
    assert transport.posted == []
    assert request.request_id in comments[1].body


def test_newer_claim_seen_during_reinspection_suppresses_recovery() -> None:
    request, initial = claim_fixture(claim_age_seconds=301)
    reinspected = [
        *initial,
        IssueComment(
            12,
            "magixhot",
            format_claim_comment(request.request_id),
            BASE_TIME,
        ),
    ]
    transport = SequencedTransport([initial, reinspected])
    worker = GitHubControlWorker(
        transport=transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )

    assert worker.poll_once() is None
    assert transport.reads == 2
    assert transport.posted == []
