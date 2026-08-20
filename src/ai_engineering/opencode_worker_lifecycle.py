"""Single-instance local worker lifecycle for AUTO-0014/AUTO-0018."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import time
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Callable, TextIO

from .control_diagnostics import ControlFailureKind
from .opencode_control_protocol import (
    ControlRequest,
    ControlResult,
    ControlResultState,
    ControlTaskClass,
)
from .opencode_control_worker import (
    GhIssueTransport,
    GitHubControlWorker,
    execute_with_failed_result,
)
from .opencode_readonly_adapter import (
    OpenCodeHttpTransport,
    ReadOnlyOpenCodeAdapter,
    RepositorySnapshot,
    capture_repository_snapshot,
)
from .opencode_service_config import ServiceRuntimeConfig, load_service_config
from .quality_gate_relay import execute_quality_verify


class WorkerLifecycleError(RuntimeError):
    """Raised when the local worker lifecycle cannot proceed safely."""


WorkerRunner = Callable[[ServiceRuntimeConfig], None]


def lifecycle_key(config: ServiceRuntimeConfig) -> str:
    """Return a portable key for one repository/control-issue worker identity."""

    material = f"{config.repository}\n{config.control_issue}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()[:24]


class SingleInstanceLock(AbstractContextManager["SingleInstanceLock"]):
    """Non-blocking process lock kept outside the repository."""

    def __init__(self, runtime_dir: Path, key: str) -> None:
        if not runtime_dir.is_absolute():
            raise WorkerLifecycleError("runtime directory must be absolute")
        if not key or any(char not in "0123456789abcdef" for char in key):
            raise WorkerLifecycleError("invalid lifecycle key")
        self._runtime_dir = runtime_dir
        self._path = runtime_dir / f"worker-{key}.lock"
        self._handle: TextIO | None = None

    @property
    def path(self) -> Path:
        return self._path

    def __enter__(self) -> "SingleInstanceLock":
        try:
            self._runtime_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            handle = self._path.open("a+", encoding="utf-8")
            os.chmod(self._path, 0o600)
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            if "handle" in locals():
                handle.close()
            raise WorkerLifecycleError("worker instance is already active") from exc
        except OSError as exc:
            if "handle" in locals():
                handle.close()
            raise WorkerLifecycleError("worker lifecycle lock unavailable") from exc
        self._handle = handle
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        handle = self._handle
        self._handle = None
        if handle is not None:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            finally:
                handle.close()
        return None


def stale_workspace_result(
    request: ControlRequest,
    snapshot: RepositorySnapshot,
) -> ControlResult:
    """Return bounded public-safe evidence for an expected-head mismatch."""

    if request.expected_head is None:
        raise ValueError("stale-workspace evidence requires expected_head")
    if snapshot.head == request.expected_head:
        raise ValueError("stale-workspace evidence requires a head mismatch")

    evidence = {
        "expected_head": request.expected_head,
        "guidance": (
            "synchronize the local checkout to the expected commit with an "
            "operator-reviewed fast-forward; no automatic repository change "
            "was performed"
        ),
        "kind": ControlFailureKind.EXPECTED_HEAD_MISMATCH.value,
        "observed_head": snapshot.head,
    }
    text = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    if len(text) > request.max_result_chars:
        raise ValueError("stale-workspace evidence exceeds request bound")

    return ControlResult(
        request_id=request.request_id,
        task_class=request.task_class,
        repository=request.repository,
        branch=snapshot.branch,
        head=snapshot.head,
        pre_clean=snapshot.is_clean,
        state=ControlResultState.FAILED,
        text=text,
        post_clean=snapshot.is_clean,
        version=request.version,
    )


def execute_configured_request(
    repository_root: Path,
    adapter: ReadOnlyOpenCodeAdapter,
    request: ControlRequest,
) -> ControlResult:
    """Execute one configured request after a non-mutating head preflight."""

    snapshot = capture_repository_snapshot(repository_root)
    if request.expected_head is not None and snapshot.head != request.expected_head:
        return stale_workspace_result(request, snapshot)
    if request.task_class is ControlTaskClass.QUALITY_VERIFY:
        return execute_quality_verify(repository_root, request)
    return execute_with_failed_result(repository_root, adapter, request)


def run_configured_worker(config: ServiceRuntimeConfig) -> None:
    """Run the bounded worker with OpenCode and exact-Quality read-only paths."""

    transport = GhIssueTransport(
        repository=config.repository,
        issue_number=config.control_issue,
    )
    opencode_transport = OpenCodeHttpTransport(
        config.server_url,
        directory=config.repository_root,
    )
    adapter = ReadOnlyOpenCodeAdapter(
        config.repository_root,
        transport=opencode_transport,
    )

    def executor(request: ControlRequest) -> ControlResult:
        return execute_configured_request(config.repository_root, adapter, request)

    worker = GitHubControlWorker(transport=transport, executor=executor)
    while True:
        worker.poll_once()
        time.sleep(config.poll_seconds)


def run_lifecycle(
    config: ServiceRuntimeConfig,
    *,
    runtime_dir: Path,
    runner: WorkerRunner = run_configured_worker,
) -> None:
    """Hold one process-level lock for the complete worker lifetime."""

    with SingleInstanceLock(runtime_dir.resolve(), lifecycle_key(config)):
        runner(config)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUTO-0014 local worker lifecycle")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--runtime-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    config = load_service_config(args.config)
    run_lifecycle(config, runtime_dir=args.runtime_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
