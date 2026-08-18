"""Single-instance local worker lifecycle for AUTO-0014."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import os
import time
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Callable

from .opencode_control_worker import (
    GhIssueTransport,
    GitHubControlWorker,
    execute_with_failed_result,
)
from .opencode_readonly_adapter import OpenCodeHttpTransport, ReadOnlyOpenCodeAdapter
from .opencode_service_config import ServiceRuntimeConfig, load_service_config


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
        self._handle = None

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
            if 'handle' in locals():
                handle.close()
            raise WorkerLifecycleError("worker instance is already active") from exc
        except OSError as exc:
            if 'handle' in locals():
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


def run_configured_worker(config: ServiceRuntimeConfig) -> None:
    """Run the existing AUTO-0013 worker with validated local bindings."""

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

    def executor(request):
        return execute_with_failed_result(config.repository_root, adapter, request)

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
