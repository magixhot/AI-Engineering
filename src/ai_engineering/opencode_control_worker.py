"""Bounded GitHub control worker for AUTO-0013/AUTO-0016/AUTO-0019."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Protocol

from .control_diagnostics import (
    ClaimRecoveryEvidence,
    ClaimRecoveryReason,
    ControlFailureKind,
    claim_recovery_evidence,
    protocol_rejection_evidence,
    serialize_claim_recovery,
    serialize_protocol_rejection,
)
from .opencode_control_protocol import (
    PROTOCOL_VERSION,
    ControlProtocolError,
    ControlRequest,
    ControlResult,
    ControlResultState,
    parse_request,
    serialize_request,
    serialize_result,
)
from .opencode_readonly_adapter import (
    OpenCodeAdapterError,
    ReadOnlyOpenCodeAdapter,
    SnapshotProvider,
    capture_repository_snapshot,
)

DEFAULT_REPOSITORY = "magixhot/AI-Engineering"
DEFAULT_CONTROL_ISSUE = 130
DEFAULT_POLL_SECONDS = 10.0
DEFAULT_READ_ATTEMPTS = 3
DEFAULT_READ_RETRY_BASE_SECONDS = 1.0
DEFAULT_RECOVERY_GRACE_SECONDS = 300.0
MIN_RECOVERY_GRACE_SECONDS = 60.0
MAX_RECOVERY_GRACE_SECONDS = 86_400.0
REQUEST_FENCE = "auto-0013-request"
CLAIM_FENCE = "auto-0013-claim"
RESULT_FENCE = "auto-0013-result"
RECOVERY_FENCE = "auto-0019-recovery"


class ControlWorkerError(RuntimeError):
    """Raised when the GitHub control worker cannot proceed safely."""


@dataclass(frozen=True, slots=True)
class IssueComment:
    comment_id: int
    author: str
    body: str
    created_at: datetime | None = None


class GitHubTransport(Protocol):
    def list_comments(self) -> list[IssueComment]: ...

    def post_comment(self, body: str) -> None: ...


Executor = Callable[[ControlRequest], ControlResult]
Sleeper = Callable[[float], None]
Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _structured_local_event(
    kind: ControlFailureKind,
    state: str,
    **safe_fields: object,
) -> str:
    payload = {"kind": kind.value, "state": state, **safe_fields}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _extract_fenced_payload(body: str, fence: str) -> str | None:
    marker = f"```{fence}\n"
    start = body.find(marker)
    if start < 0:
        return None
    start += len(marker)
    end = body.find("\n```", start)
    if end < 0 or body.find(marker, end + 4) >= 0:
        return None
    return body[start:end]


def format_request_comment(request: ControlRequest) -> str:
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


def format_recovery_comment(evidence: ClaimRecoveryEvidence) -> str:
    """Format bounded fail-closed terminalization evidence without repo snapshots."""

    payload = json.loads(serialize_claim_recovery(evidence))
    payload.update({"state": "FAILED", "version": PROTOCOL_VERSION})
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"```{RECOVERY_FENCE}\n{encoded}\n```"


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


def _strict_claim_request_id(body: str) -> str | None:
    payload = _extract_fenced_payload(body, CLAIM_FENCE)
    if payload is None:
        return None
    try:
        value = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict) or set(value) != {"request_id", "state"}:
        return None
    if value.get("state") != "CLAIMED":
        return None
    request_id = value.get("request_id")
    return request_id if isinstance(request_id, str) else None


def _strict_recovery_request_id(body: str) -> str | None:
    payload = _extract_fenced_payload(body, RECOVERY_FENCE)
    if payload is None:
        return None
    try:
        value = json.loads(payload)
    except json.JSONDecodeError:
        return None
    expected_keys = {
        "kind",
        "reason",
        "replay_attempted",
        "repository",
        "request_id",
        "state",
        "task_class",
        "version",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        return None
    if value.get("kind") != ControlFailureKind.CLAIM_RECOVERY_REQUIRED.value:
        return None
    if value.get("reason") != ClaimRecoveryReason.CLAIMED_WITHOUT_TERMINAL_RESULT.value:
        return None
    if value.get("replay_attempted") is not False or value.get("state") != "FAILED":
        return None
    if value.get("version") != PROTOCOL_VERSION:
        return None
    request_id = value.get("request_id")
    return request_id if isinstance(request_id, str) else None


def _terminal_request_ids(comments: Iterable[IssueComment]) -> set[str]:
    terminal: set[str] = set()
    for comment in comments:
        request_id = _request_id_from_envelope(comment.body, RESULT_FENCE)
        if request_id is not None:
            terminal.add(request_id)
        recovery_id = _strict_recovery_request_id(comment.body)
        if recovery_id is not None:
            terminal.add(recovery_id)
    return terminal


def _safe_adapter_detail(message: str) -> str | None:
    safe_exact = {
        "repository identity mismatch",
        "workspace must be clean before execution",
        "expected HEAD does not match workspace",
        "OpenCode server unavailable",
        "OpenCode returned malformed JSON",
        "OpenCode returned a non-object response",
        "OpenCode did not return a session id",
        "OpenCode response has no parts list",
        "OpenCode response contains no textual result",
        "repository invariant changed during OpenCode execution",
    }
    if message in safe_exact or message.startswith("OpenCode HTTP error: "):
        return message
    return None


def _public_failure_summary(exc: Exception) -> str:
    """Return a bounded public-safe failure summary without local details."""

    if isinstance(exc, OpenCodeAdapterError):
        message = str(exc)
        safe = _safe_adapter_detail(message)
        if safe is not None:
            return safe

        for prefix in (
            "OpenCode session creation failed: ",
            "OpenCode message execution failed: ",
        ):
            if message.startswith(prefix):
                detail = _safe_adapter_detail(message[len(prefix) :])
                if detail is not None:
                    return prefix + detail

        return "OpenCode adapter failed closed"
    return "Read-only execution failed closed"


def execute_with_failed_result(
    repository_path: Path,
    adapter: ReadOnlyOpenCodeAdapter,
    request: ControlRequest,
    *,
    snapshot_provider: SnapshotProvider | None = None,
) -> ControlResult:
    """Convert post-claim execution failures into terminal typed evidence."""

    provider = snapshot_provider or (
        lambda: capture_repository_snapshot(repository_path)
    )
    before = provider()
    try:
        return adapter.execute(request)
    except Exception as exc:
        print(
            f"AUTO-0013 local execution failure: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        try:
            after = provider()
            post_clean = after.is_clean
        except Exception as snapshot_exc:
            print(
                "AUTO-0013 post-failure snapshot error: "
                f"{type(snapshot_exc).__name__}: {snapshot_exc}",
                file=sys.stderr,
            )
            after = before
            post_clean = False

        text = _public_failure_summary(exc)
        if len(text) > request.max_result_chars:
            text = text[: request.max_result_chars]
        return ControlResult(
            request_id=request.request_id,
            task_class=request.task_class,
            repository=request.repository,
            branch=after.branch,
            head=after.head,
            pre_clean=before.is_clean,
            state=ControlResultState.FAILED,
            text=text,
            post_clean=post_clean,
            version=request.version,
        )


class GhIssueTransport:
    """GitHub issue transport implemented through authenticated `gh`."""

    def __init__(
        self,
        *,
        repository: str = DEFAULT_REPOSITORY,
        issue_number: int = DEFAULT_CONTROL_ISSUE,
        read_attempts: int = DEFAULT_READ_ATTEMPTS,
        read_retry_base_seconds: float = DEFAULT_READ_RETRY_BASE_SECONDS,
        sleeper: Sleeper = time.sleep,
    ) -> None:
        if read_attempts < 1:
            raise ControlWorkerError("read attempts must be at least one")
        if read_retry_base_seconds < 0:
            raise ControlWorkerError("read retry base must not be negative")
        self._repository = repository
        self._issue_number = issue_number
        self._read_attempts = read_attempts
        self._read_retry_base_seconds = read_retry_base_seconds
        self._sleeper = sleeper

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
            raise ControlWorkerError("GitHub request failed") from exc
        except FileNotFoundError as exc:
            raise ControlWorkerError("gh executable not found") from exc
        return completed.stdout

    def _read_pages(self, endpoint: str) -> list[object]:
        last_error: ControlWorkerError | None = None
        for attempt in range(1, self._read_attempts + 1):
            try:
                raw = self._run("api", "--paginate", "--slurp", endpoint)
                try:
                    pages = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ControlWorkerError(
                        "GitHub returned malformed JSON"
                    ) from exc
                if not isinstance(pages, list):
                    raise ControlWorkerError(
                        "GitHub comments response is not paginated"
                    )
                return pages
            except ControlWorkerError as exc:
                last_error = exc
                if attempt >= self._read_attempts:
                    break
                print(
                    _structured_local_event(
                        ControlFailureKind.TRANSPORT_READ_FAILURE,
                        "retrying",
                        attempt=attempt,
                        next_delay_seconds=self._read_retry_base_seconds * attempt,
                    ),
                    file=sys.stderr,
                )
                self._sleeper(self._read_retry_base_seconds * attempt)
        assert last_error is not None
        raise last_error

    def list_comments(self) -> list[IssueComment]:
        endpoint = (
            f"repos/{self._repository}/issues/{self._issue_number}/comments"
            "?per_page=100"
        )
        pages = self._read_pages(endpoint)

        comments: list[IssueComment] = []
        for page in pages:
            if not isinstance(page, list):
                raise ControlWorkerError("GitHub comments page is not a list")
            for item in page:
                if not isinstance(item, dict):
                    continue
                user = item.get("user")
                if not isinstance(user, dict):
                    continue
                comment_id = item.get("id")
                author = user.get("login")
                body = item.get("body")
                created_at_raw = item.get("created_at")
                if not isinstance(comment_id, int):
                    continue
                if not isinstance(author, str) or not isinstance(body, str):
                    continue
                created_at: datetime | None = None
                if isinstance(created_at_raw, str):
                    try:
                        created_at = datetime.fromisoformat(
                            created_at_raw.replace("Z", "+00:00")
                        )
                    except ValueError:
                        created_at = None
                comments.append(IssueComment(comment_id, author, body, created_at))
        return comments

    def post_comment(self, body: str) -> None:
        """Publish once; writes are intentionally not retried to avoid duplicates."""

        endpoint = f"repos/{self._repository}/issues/{self._issue_number}/comments"
        self._run("api", "--method", "POST", endpoint, "-f", f"body={body}")


class GitHubControlWorker:
    """Claim/execute new work and terminalize aged unresolved claims without replay."""

    def __init__(
        self,
        *,
        transport: GitHubTransport,
        executor: Executor,
        trusted_authors: Iterable[str] = ("magixhot",),
        recovery_grace_seconds: float = DEFAULT_RECOVERY_GRACE_SECONDS,
        clock: Clock = _utc_now,
    ) -> None:
        if not MIN_RECOVERY_GRACE_SECONDS <= recovery_grace_seconds <= MAX_RECOVERY_GRACE_SECONDS:
            raise ControlWorkerError("recovery grace interval is outside allowed bounds")
        self._transport = transport
        self._executor = executor
        self._trusted_authors = frozenset(trusted_authors)
        self._recovery_grace_seconds = recovery_grace_seconds
        self._clock = clock
        self._transport_read_failed = False

    def _list_comments_fail_closed(self) -> list[IssueComment] | None:
        try:
            comments = self._transport.list_comments()
        except ControlWorkerError:
            if not self._transport_read_failed:
                print(
                    _structured_local_event(
                        ControlFailureKind.TRANSPORT_READ_FAILURE,
                        "failed_closed",
                    ),
                    file=sys.stderr,
                )
            self._transport_read_failed = True
            return None
        if self._transport_read_failed:
            print(
                _structured_local_event(
                    ControlFailureKind.SUCCESS,
                    "transport_recovered",
                ),
                file=sys.stderr,
            )
            self._transport_read_failed = False
        return comments

    def _trusted(self, comments: Iterable[IssueComment]) -> list[IssueComment]:
        return [
            comment
            for comment in comments
            if comment.author in self._trusted_authors
        ]

    def _valid_requests(
        self, comments: Iterable[IssueComment]
    ) -> dict[str, tuple[IssueComment, ControlRequest]]:
        valid: dict[str, tuple[IssueComment, ControlRequest]] = {}
        for comment in comments:
            payload = _extract_fenced_payload(comment.body, REQUEST_FENCE)
            if payload is None:
                continue
            try:
                request = parse_request(payload)
            except ControlProtocolError as exc:
                evidence = protocol_rejection_evidence(
                    comment_id=comment.comment_id,
                    exc=exc,
                )
                print(serialize_protocol_rejection(evidence), file=sys.stderr)
                continue
            valid.setdefault(request.request_id, (comment, request))
        return valid

    def _latest_claims(
        self, comments: Iterable[IssueComment]
    ) -> dict[str, IssueComment]:
        claims: dict[str, IssueComment] = {}
        for comment in comments:
            request_id = _strict_claim_request_id(comment.body)
            if request_id is not None:
                claims[request_id] = comment
        return claims

    def _claim_is_aged(self, claim: IssueComment) -> bool:
        if claim.created_at is None or claim.created_at.tzinfo is None:
            return False
        now = self._clock()
        if now.tzinfo is None:
            raise ControlWorkerError("recovery clock must be timezone-aware")
        age_seconds = (now - claim.created_at).total_seconds()
        return age_seconds >= self._recovery_grace_seconds

    def _recover_one_aged_claim(
        self,
        trusted_comments: list[IssueComment],
    ) -> str | None:
        valid_requests = self._valid_requests(trusted_comments)
        terminal = _terminal_request_ids(trusted_comments)
        latest_claims = self._latest_claims(trusted_comments)

        for request_id, claim in latest_claims.items():
            if request_id in terminal or not self._claim_is_aged(claim):
                continue
            origin = valid_requests.get(request_id)
            if origin is None:
                continue
            request_comment, request = origin
            if request_comment.comment_id >= claim.comment_id:
                continue

            reinspected = self._list_comments_fail_closed()
            if reinspected is None:
                return None
            trusted_reinspection = self._trusted(reinspected)
            if request_id in _terminal_request_ids(trusted_reinspection):
                return None
            current_claim = self._latest_claims(trusted_reinspection).get(request_id)
            if current_claim is None or current_claim.comment_id != claim.comment_id:
                return None
            current_requests = self._valid_requests(trusted_reinspection)
            current_origin = current_requests.get(request_id)
            if current_origin is None or current_origin[0].comment_id >= claim.comment_id:
                return None

            evidence = claim_recovery_evidence(
                request_id=request.request_id,
                task_class=request.task_class,
                repository=request.repository,
            )
            self._transport.post_comment(format_recovery_comment(evidence))
            return request_id
        return None

    def poll_once(self) -> str | None:
        comments = self._list_comments_fail_closed()
        if comments is None:
            return None
        trusted_comments = self._trusted(comments)

        recovered = self._recover_one_aged_claim(trusted_comments)
        if recovered is not None:
            return recovered

        completed_or_claimed = _terminal_request_ids(trusted_comments)
        completed_or_claimed.update(
            request_id
            for comment in trusted_comments
            if (request_id := _strict_claim_request_id(comment.body)) is not None
        )

        for comment in trusted_comments:
            payload = _extract_fenced_payload(comment.body, REQUEST_FENCE)
            if payload is None:
                continue
            try:
                request = parse_request(payload)
            except ControlProtocolError as exc:
                evidence = protocol_rejection_evidence(
                    comment_id=comment.comment_id,
                    exc=exc,
                )
                print(serialize_protocol_rejection(evidence), file=sys.stderr)
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
    if poll_seconds < 1.0:
        raise ControlWorkerError("poll interval must be at least one second")

    repository_path = repository_path.resolve()
    transport = GhIssueTransport()
    adapter = ReadOnlyOpenCodeAdapter(repository_path)

    def executor(request: ControlRequest) -> ControlResult:
        return execute_with_failed_result(repository_path, adapter, request)

    worker = GitHubControlWorker(transport=transport, executor=executor)
    print(
        _structured_local_event(ControlFailureKind.SUCCESS, "polling_started"),
        file=sys.stderr,
    )

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
