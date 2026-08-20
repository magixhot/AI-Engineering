from __future__ import annotations

from ai_engineering.opencode_control_protocol import ControlRequest, ControlResult
from ai_engineering.opencode_control_worker import (
    ControlWorkerError,
    GhIssueTransport,
    GitHubControlWorker,
    IssueComment,
)


class RetryReadTransport(GhIssueTransport):
    def __init__(self) -> None:
        self.calls = 0
        self.sleeps: list[float] = []
        super().__init__(
            read_attempts=3,
            read_retry_base_seconds=0.5,
            sleeper=self.sleeps.append,
        )

    def _run(self, *args: str) -> str:
        self.calls += 1
        if self.calls < 3:
            raise ControlWorkerError("private transport detail must stay local")
        return "[[]]"


class AlwaysFailReadTransport:
    def list_comments(self) -> list[IssueComment]:
        raise ControlWorkerError("private transport detail must stay local")

    def post_comment(self, body: str) -> None:
        raise AssertionError("unexpected write")


class RecoveringReadTransport:
    def __init__(self) -> None:
        self.calls = 0

    def list_comments(self) -> list[IssueComment]:
        self.calls += 1
        if self.calls == 1:
            raise ControlWorkerError("private transport detail must stay local")
        return []

    def post_comment(self, body: str) -> None:
        raise AssertionError("unexpected write")


class MalformedRequestTransport:
    def list_comments(self) -> list[IssueComment]:
        return [
            IssueComment(
                42,
                "magixhot",
                "```auto-0013-request\n{private invalid payload\n```",
            )
        ]

    def post_comment(self, body: str) -> None:
        raise AssertionError("unexpected write")


def never_execute(request: ControlRequest) -> ControlResult:
    raise AssertionError(f"unexpected execution: {request.request_id}")


def test_read_transport_retries_with_bounded_deterministic_backoff(capsys) -> None:
    transport = RetryReadTransport()

    assert transport.list_comments() == []
    assert transport.calls == 3
    assert transport.sleeps == [0.5, 1.0]

    stderr = capsys.readouterr().err
    assert '"kind":"transport_read_failure"' in stderr
    assert '"state":"retrying"' in stderr
    assert "private transport detail" not in stderr


def test_worker_contains_transport_read_failure_without_chatter(capsys) -> None:
    worker = GitHubControlWorker(
        transport=AlwaysFailReadTransport(),
        executor=never_execute,
    )

    assert worker.poll_once() is None
    assert worker.poll_once() is None

    stderr = capsys.readouterr().err
    assert stderr.count('"state":"failed_closed"') == 1
    assert "private transport detail" not in stderr


def test_worker_emits_single_recovery_transition(capsys) -> None:
    worker = GitHubControlWorker(
        transport=RecoveringReadTransport(),
        executor=never_execute,
    )

    assert worker.poll_once() is None
    assert worker.poll_once() is None
    assert worker.poll_once() is None

    stderr = capsys.readouterr().err
    assert stderr.count('"state":"failed_closed"') == 1
    assert stderr.count('"state":"transport_recovered"') == 1


def test_protocol_rejection_is_visible_without_echoing_payload(capsys) -> None:
    worker = GitHubControlWorker(
        transport=MalformedRequestTransport(),
        executor=never_execute,
    )

    assert worker.poll_once() is None

    stderr = capsys.readouterr().err
    assert '"comment_id":42' in stderr
    assert '"kind":"protocol_rejection"' in stderr
    assert '"reason":"malformed_json"' in stderr
    assert "private invalid payload" not in stderr


def test_retry_configuration_fails_closed() -> None:
    try:
        GhIssueTransport(read_attempts=0)
    except ControlWorkerError as exc:
        assert "read attempts" in str(exc)
    else:
        raise AssertionError("expected ControlWorkerError")

    try:
        GhIssueTransport(read_retry_base_seconds=-1)
    except ControlWorkerError as exc:
        assert "read retry base" in str(exc)
    else:
        raise AssertionError("expected ControlWorkerError")
