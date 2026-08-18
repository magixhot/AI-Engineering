"""Bounded GitHub control worker for AUTO-0013."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol

from .opencode_control_protocol import (
    ControlProtocolError,
    ControlRequest,
    ControlResult,
    parse_request,
    serialize_result,
)
from .opencode_readonly_adapter import ReadOnlyOpenCodeAdapter

DEFAULT_REPOSITORY = "magixhot/AI-Engineering"
DEFAULT_CONTROL_ISSUE = 130
DEFAULT_POLL_SECONDS = 10.0
REQUEST_FENCE = "auto-0013-request"
CLAIM_FENCE = "auto-0013-claim"
RESULT_FENCE = "auto-0013-result"


class ControlWorkerError(RuntimeError):
    """Raised when the GitHub control worker cannot proceed safely."""


@dataclass(frozen=True, slots=True)
class IssueComment:
    comment_id: int
    author: str
    body: str


class GitHubTransport(Protocol):
    def list_comments(self) -> list[IssueComment]: ...

    def post_comment(self, body: str) -> None: ...


Executor = Callable[[ControlRequest], ControlResult]


def _extract_fenced_payload(body: str, fence: str) -> str | None:
    marker = f"```{fence}\n"
    start = body.find(marker)
    if start < 0:
        return None
    start += len(marker)
    end = body.find("\n```", start)
    if end < 0:
        return None
    if body.find(marker, end + 4) >= 0:
        return None
    return body[start:end]


def format_request_comment(request: ControlRequest) -> str:
    """Return the canonical public comment envelope for a request."""

    from .opencode_control_protocol import serialize_request

    payload = serialize_request(request).decode("utf-8")
    return f"```{REQUEST_FENCE}\n{payload}\n```"


def format_claim_comment(request_id: str) -> str:
    payload = json.dumps(
        {"request_id": request_id, "state": "CLAIMED"},
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"```{CLAIM_FENCE}\n{payload}\n```"


def format_result_comment(result: ControlResult) -> str:
    payload = serialize_result(result).decode("utf-8")
    return f"```{RESULT_FENCE}\n{payload}\n```"


def _request_id_from_envelope(body: str, fence: str) -> str | None:
    payload = _extract_fenced_payload(body, fence)
    if payload is None:
        return None
    try:
        value = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    request_id = value.get("request_id")
    return request_id if isinstance(request_id, str) else None


class GhIssueTransport:
    """GitHub issue transport implemented through the authenticated `gh` CLI."""

    def __init__(
        self,
        *,
        repository: str = DEFAULT_REPOSITORY,
        issue_number: int = DEFAULT_CONTROL_ISSUE,
    ) -> None:
        self._repository = repository
        self._issue_number = issue_number

    def _run(self, *args: str) -> str:
        try:
            completed = subprocess.run(
                ["gh", *args],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise ControlWorkerError("GitHub request timed out") from exc
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip() or "GitHub request failed"
            raise ControlWorkerError(detail) from exc
        except FileNotFoundError as exc:
            raise ControlWorkerError("gh executable not found") from exc
        return completed.stdout

    def list_comments(self) -> list[IssueComment]:
        endpoint = (
            f"repos/{self._repository}/issues/{self._issue_number}/comments"
            "?per_page=100"
        )
        raw = self._run("api", endpoint)
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ControlWorkerError("GitHub returned malformed JSON") from exc
        if not isinstance(value, list):
            raise ControlWorkerError("GitHub comments response is not a list")

        comments: list[IssueComment] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            user = item.get("user")
            if not isinstance(user, dict):
                continue
            comment_id = item.get("id")
            author = user.get("login")
            body = item.get("body")
            if not isinstance(comment_id, int):
                continue
            if not isinstance(author, str) or not isinstance(body, str):
                continue
            comments.append(IssueComment(comment_id, author, body))
        return comments

    def post_comment(self, body: str) -> None:
        endpoint = f"repos/{self._repository}/issues/{self._issue_number}/comments"
        self._run("api", "--method", "POST", endpoint, "-f", f"body={body}")


class GitHubControlWorker:
    """Claim and execute at most one new valid read-only request per poll."""

    def __init__(
        self,
        *,
        transport: GitHubTransport,
        executor: Executor,
        trusted_authors: Iterable[str] = ("magixhot",),
    ) -> None:
        self._transport = transport
        self._executor = executor
        self._trusted_authors = frozenset(trusted_authors)

    def poll_once(self) -> str | None:
        comments = self._transport.list_comments()
        completed_or_claimed = {
            request_id
            for comment in comments
            for fence in (CLAIM_FENCE, RESULT_FENCE)
            if (request_id := _request_id_from_envelope(comment.body, fence))
            is not None
        }

        for comment in comments:
            if comment.author not in self._trusted_authors:
                continue
            payload = _extract_fenced_payload(comment.body, REQUEST_FENCE)
            if payload is None:
                continue
            try:
                request = parse_request(payload)
            except ControlProtocolError:
                continue
            if request.request_id in completed_or_claimed:
                continue

            self._transport.post_comment(format_claim_comment(request.request_id))
            result = self._executor(request)
            self._transport.post_comment(format_result_comment(result))
            return request.request_id
        return None


def run_worker(
    repository_path: Path,
    *,
    poll_seconds: float = DEFAULT_POLL_SECONDS,
    once: bool = False,
) -> None:
    """Run the bounded local worker."""

    if poll_seconds < 1.0:
        raise ControlWorkerError("poll interval must be at least one second")

    transport = GhIssueTransport()
    adapter = ReadOnlyOpenCodeAdapter(repository_path)
    worker = GitHubControlWorker(transport=transport, executor=adapter.execute)

    while True:
        worker.poll_once()
        if once:
            return
        time.sleep(poll_seconds)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUTO-0013 GitHub control worker")
    parser.add_argument("repository", type=Path)
    parser.add_argument("--poll-seconds", type=float, default=DEFAULT_POLL_SECONDS)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)
    run_worker(args.repository, poll_seconds=args.poll_seconds, once=args.once)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
