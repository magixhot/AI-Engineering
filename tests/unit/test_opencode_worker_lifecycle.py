from __future__ import annotations

import os
from pathlib import Path

import pytest

from ai_engineering.opencode_service_config import ServiceRuntimeConfig
from ai_engineering.opencode_worker_lifecycle import (
    SingleInstanceLock,
    WorkerLifecycleError,
    lifecycle_key,
    run_lifecycle,
)

requires_posix_lock = pytest.mark.skipif(
    os.name == "nt",
    reason="worker lifecycle locking is the POSIX fcntl contract used by WSL/Linux",
)


def make_config(root: Path) -> ServiceRuntimeConfig:
    return ServiceRuntimeConfig(
        repository_root=root,
        repository="magixhot/AI-Engineering",
        control_issue=130,
        server_url="http://127.0.0.1:4096",
        poll_seconds=10.0,
    )


def test_lifecycle_key_is_deterministic_and_path_independent(tmp_path: Path) -> None:
    first = make_config(tmp_path / "one")
    second = make_config(tmp_path / "two")

    assert lifecycle_key(first) == lifecycle_key(second)
    assert len(lifecycle_key(first)) == 24


@requires_posix_lock
def test_single_instance_lock_rejects_second_active_instance(tmp_path: Path) -> None:
    runtime_dir = (tmp_path / "runtime").resolve()
    key = "a" * 24

    with SingleInstanceLock(runtime_dir, key) as first:
        assert first.path.exists()
        with pytest.raises(WorkerLifecycleError, match="already active"):
            with SingleInstanceLock(runtime_dir, key):
                pass


@requires_posix_lock
def test_lock_is_reacquirable_after_clean_exit(tmp_path: Path) -> None:
    runtime_dir = (tmp_path / "runtime").resolve()
    key = "b" * 24

    with SingleInstanceLock(runtime_dir, key):
        pass
    with SingleInstanceLock(runtime_dir, key):
        pass


@requires_posix_lock
def test_lifecycle_invokes_runner_once_under_lock(tmp_path: Path) -> None:
    config = make_config((tmp_path / "repo").resolve())
    runtime_dir = (tmp_path / "runtime").resolve()
    received: list[ServiceRuntimeConfig] = []

    def runner(value: ServiceRuntimeConfig) -> None:
        received.append(value)
        lock_path = runtime_dir / f"worker-{lifecycle_key(value)}.lock"
        assert lock_path.exists()

    run_lifecycle(config, runtime_dir=runtime_dir, runner=runner)

    assert received == [config]


def test_lifecycle_rejects_relative_runtime_directory(tmp_path: Path) -> None:
    config = make_config((tmp_path / "repo").resolve())

    with pytest.raises(WorkerLifecycleError, match="absolute"):
        with SingleInstanceLock(Path("relative-runtime"), lifecycle_key(config)):
            pass
