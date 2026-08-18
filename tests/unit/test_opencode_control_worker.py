from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Iterable

from ai_engineering.opencode_control_protocol import (
    ControlRequest,
    ControlResult,
    ControlResultState,
    ControlTaskClass,
    build_request,
)
from ai_engineering.opencode_control_worker import (
    CLAIM_FENCE,
    RESULT_FENCE,
    GitHubControlWorker,
    IssueComment,
    execute_with_failed_result,
    format_claim_comment,
    format_request_comment,
    format_result_comment,
)
from ai_engineering.opencode_readonly_adapter import (
    OpenCodeAdapterError,
    ReadOnlyOpenCodeAdapter,
    RepositorySnapshot,
)

REPOSITORY = "magixhot/AI-Engineering"
HEAD = "bf3c485afd2ce8d53cf606844f9185ecb6827447"


class FakeTransport:
    def __init__(self, comments: Iterable[IssueComment]) -> None:
        self.comments = list(comments)
        self.posted: list[str] = []

    def list_comments(self) -> list[IssueComment]:
        return list(self.comments)

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


def make_snapshot(*, status: str = "") -> RepositorySnapshot:
    return RepositorySnapshot(
        branch="master",
        head=HEAD,
        status=status,
        index_state_hash="index",
        worktree_diff_hash="worktree",
        cached_diff_hash="cached",
        local_config_hash="config",
        remotes_hash="remotes",
    )


def never_execute(request: ControlRequest) -> ControlResult:
    raise AssertionError(f"unexpected execution: {request.request_id}")


def test_worker_claims_executes_and_posts_result_once() -> None:
    request = make_request()
    transport = FakeTransport(
        [IssueComment(1, "magixhot", format_request_comment(request))]
    )
    executed: list[ControlRequest] = []

    def executor(received: ControlRequest) -> ControlResult:
        executed.append(received)
        return make_result(received)

    worker = GitHubControlWorker(transport=transport, executor=executor)

    assert worker.poll_once() == request.request_id
    assert executed == [request]
    assert len(transport.posted) == 2
    assert transport.posted[0].startswith(f"```{CLAIM_FENCE}\n")
    assert transport.posted[1].startswith(f"```{RESULT_FENCE}\n")


def test_worker_ignores_untrusted_author() -> None:
    request = make_request()
    transport = FakeTransport(
        [IssueComment(1, "someone-else", format_request_comment(request))]
    )
    worker = GitHubControlWorker(transport=transport, executor=never_execute)

    assert worker.poll_once() is None
    assert transport.posted == []


def test_worker_ignores_untrusted_forged_claim() -> None:
    request = make_request()
    transport = FakeTransport(
        [
            IssueComment(1, "magixhot", format_request_comment(request)),
            IssueComment(
                2,
                "someone-else",
                format_claim_comment(request.request_id),
            ),
        ]
    )
    worker = GitHubControlWorker(
        transport=transport,
        executor=lambda received: make_result(received),
    )

    assert worker.poll_once() == request.request_id
    assert len(transport.posted) == 2


def test_worker_ignores_malformed_and_write_capable_request() -> None:
    request = make_request()
    malformed = "```auto-0013-request\nnot json\n```"
    write_capable = format_request_comment(request).replace(
        '"task_class":"status"',
        '"task_class":"push"',
    )
    transport = FakeTransport(
        [
            IssueComment(1, "magixhot", malformed),
            IssueComment(2, "magixhot", write_capable),
        ]
    )
    worker = GitHubControlWorker(transport=transport, executor=never_execute)

    assert worker.poll_once() is None
    assert transport.posted == []


def test_worker_suppresses_request_with_existing_claim() -> None:
    request = make_request()
    transport = FakeTransport(
        [
            IssueComment(1, "magixhot", format_request_comment(request)),
            IssueComment(2, "magixhot", format_claim_comment(request.request_id)),
        ]
    )
    worker = GitHubControlWorker(transport=transport, executor=never_execute)

    assert worker.poll_once() is None
    assert transport.posted == []


def test_worker_suppresses_request_with_existing_result() -> None:
    request = make_request()
    result = make_result(request)
    transport = FakeTransport(
        [
            IssueComment(1, "magixhot", format_request_comment(request)),
            IssueComment(2, "magixhot", format_result_comment(result)),
        ]
    )
    worker = GitHubControlWorker(transport=transport, executor=never_execute)

    assert worker.poll_once() is None
    assert transport.posted == []


def test_worker_skips_forged_request_id() -> None:
    request = make_request()
    forged = replace(request, request_id="sha256:" + "0" * 64)
    body = format_request_comment(request).replace(
        request.request_id,
        forged.request_id,
    )
    transport = FakeTransport([IssueComment(1, "magixhot", body)])
    worker = GitHubControlWorker(transport=transport, executor=never_execute)

    assert worker.poll_once() is None
    assert transport.posted == []


def test_execution_failure_becomes_typed_failed_result(capsys) -> None:
    request = make_request()
    snapshot = make_snapshot()

    def snapshot_provider() -> RepositorySnapshot:
        return snapshot

    def failing_transport(path, payload):
        raise OpenCodeAdapterError("OpenCode server unavailable")

    adapter = ReadOnlyOpenCodeAdapter(
        Path("/unused"),
        transport=failing_transport,
        snapshot_provider=snapshot_provider,
    )

    result = execute_with_failed_result(
        Path("/unused"),
        adapter,
        request,
        snapshot_provider=snapshot_provider,
    )

    assert result.state is ControlResultState.FAILED
    assert result.request_id == request.request_id
    assert result.branch == "master"
    assert result.head == HEAD
    assert result.pre_clean is True
    assert result.post_clean is True
    assert result.text == "OpenCode server unavailable"
    assert "OpenCode server unavailable" in capsys.readouterr().err


def test_failure_summary_redacts_unapproved_adapter_detail(capsys) -> None:
    request = make_request()
    snapshot = make_snapshot()

    def snapshot_provider() -> RepositorySnapshot:
        return snapshot

    def failing_transport(path, payload):
        raise OpenCodeAdapterError("private local path /home/example leaked")

    adapter = ReadOnlyOpenCodeAdapter(
        Path("/unused"),
        transport=failing_transport,
        snapshot_provider=snapshot_provider,
    )

    result = execute_with_failed_result(
        Path("/unused"),
        adapter,
        request,
        snapshot_provider=snapshot_provider,
    )

    assert result.state is ControlResultState.FAILED
    assert result.text == "OpenCode adapter failed closed"
    assert "/home/example" not in result.text
    assert "/home/example" in capsys.readouterr().err


def test_post_failure_snapshot_error_sets_post_clean_false(capsys) -> None:
    request = make_request()
    snapshot = make_snapshot()
    calls = 0

    def snapshot_provider() -> RepositorySnapshot:
        nonlocal calls
        calls += 1
        if calls >= 3:
            raise OpenCodeAdapterError("post snapshot failed")
        return snapshot

    def failing_transport(path, payload):
        raise OpenCodeAdapterError("OpenCode server unavailable")

    adapter = ReadOnlyOpenCodeAdapter(
        Path("/unused"),
        transport=failing_transport,
        snapshot_provider=snapshot_provider,
    )

    result = execute_with_failed_result(
        Path("/unused"),
        adapter,
        request,
        snapshot_provider=snapshot_provider,
    )

    assert result.state is ControlResultState.FAILED
    assert result.pre_clean is True
    assert result.post_clean is False
    assert "post-failure snapshot error" in capsys.readouterr().err
