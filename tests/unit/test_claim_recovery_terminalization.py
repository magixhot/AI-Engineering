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
    ControlWorkerError,
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


class SharedCommentChannel:
    def __init__(self, comments: Iterable[IssueComment]) -> None:
        self.comments = list(comments)
        self.posted: list[str] = []

    def publish(self, body: str) -> None:
        self.posted.append(body)
        self.comments.append(
            IssueComment(
                self.comments[-1].comment_id + 1,
                "magixhot",
                body,
                BASE_TIME,
            )
        )


class StaleFirstReadTransport:
    def __init__(
        self,
        channel: SharedCommentChannel,
        initial: Iterable[IssueComment],
    ) -> None:
        self._channel = channel
        self._initial = list(initial)
        self.reads = 0

    def list_comments(self) -> list[IssueComment]:
        self.reads += 1
        if self.reads == 1:
            return list(self._initial)
        return list(self._channel.comments)

    def post_comment(self, body: str) -> None:
        self._channel.publish(body)


class AmbiguousPostTransport(SequencedTransport):
    def __init__(
        self,
        batches: Iterable[Iterable[IssueComment]],
        *,
        write_before_error: bool,
    ) -> None:
        super().__init__(batches)
        self._write_before_error = write_before_error
        self.post_attempts = 0

    def post_comment(self, body: str) -> None:
        self.post_attempts += 1
        if self._write_before_error:
            self.posted.append(body)
        raise ControlWorkerError("private transport failure detail")


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


def test_sequential_workers_reinspect_shared_channel_before_publication() -> None:
    request, initial = claim_fixture(claim_age_seconds=301)
    channel = SharedCommentChannel(initial)
    first_transport = StaleFirstReadTransport(channel, initial)
    second_transport = StaleFirstReadTransport(channel, initial)
    first_worker = GitHubControlWorker(
        transport=first_transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )
    second_worker = GitHubControlWorker(
        transport=second_transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )

    assert first_worker.poll_once() == request.request_id
    assert second_worker.poll_once() is None
    assert first_transport.reads == 2
    assert second_transport.reads == 2
    assert len(channel.posted) == 1


def test_ambiguous_before_write_is_fenced_without_retry(
    capsys: object,
) -> None:
    request, comments = claim_fixture(claim_age_seconds=301)
    transport = AmbiguousPostTransport(
        [comments, comments],
        write_before_error=False,
    )
    worker = GitHubControlWorker(
        transport=transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )

    assert worker.poll_once() is None
    assert worker.poll_once() is None
    assert transport.post_attempts == 1
    assert transport.posted == []
    diagnostic = capsys.readouterr().err  # type: ignore[attr-defined]
    assert diagnostic.count("claim_recovery_publication_ambiguous") == 1
    assert '"state":"failed_closed"' in diagnostic
    assert request.request_id in diagnostic
    assert "private transport failure detail" not in diagnostic


def test_ambiguous_after_write_is_fenced_without_retry(
    capsys: object,
) -> None:
    request, comments = claim_fixture(claim_age_seconds=301)
    transport = AmbiguousPostTransport(
        [comments, comments],
        write_before_error=True,
    )
    worker = GitHubControlWorker(
        transport=transport,
        executor=never_execute,
        recovery_grace_seconds=300,
        clock=lambda: BASE_TIME,
    )

    assert worker.poll_once() is None
    assert worker.poll_once() is None
    assert transport.post_attempts == 1
    assert len(transport.posted) == 1
    assert transport.posted[0].startswith(f"```{RECOVERY_FENCE}\n")
    diagnostic = capsys.readouterr().err  # type: ignore[attr-defined]
    assert diagnostic.count("claim_recovery_publication_ambiguous") == 1
    assert '"state":"failed_closed"' in diagnostic
    assert request.request_id in diagnostic
    assert "private transport failure detail" not in diagnostic
