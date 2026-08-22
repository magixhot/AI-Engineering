from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest

fcntl = pytest.importorskip(
    "fcntl",
    reason="local OpenCode guard uses the POSIX bash/flock/fcntl workstation contract",
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "local-opencode-run.sh"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _make_repo(tmp_path: Path, branch: str = "feature/test") -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", branch], cwd=repo, check=True)
    _git(repo, "config", "user.name", "Guard Test")
    _git(repo, "config", "user.email", "guard@example.invalid")
    (repo / "README.md").write_text("guard test\n", encoding="utf-8")
    scripts = repo / "scripts"
    scripts.mkdir()
    (scripts / "local-opencode-run.sh").write_text(
        SCRIPT.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")
    return repo


def _fake_opencode(tmp_path: Path, body: str = "exit 0") -> Path:
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir(exist_ok=True)
    command = fake_bin / "opencode"
    command.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n" + body + "\n",
        encoding="utf-8",
    )
    command.chmod(0o755)
    return fake_bin


def _run(
    repo: Path,
    tmp_path: Path,
    *args: str,
    fake_body: str = "exit 0",
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    runtime = tmp_path / "runtime"
    runtime.mkdir(exist_ok=True)
    fake_bin = _fake_opencode(tmp_path, fake_body)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["XDG_RUNTIME_DIR"] = str(runtime)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", "scripts/local-opencode-run.sh", *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _lock_path(repo: Path, runtime: Path) -> Path:
    key = hashlib.sha256(str(repo).encode()).hexdigest()
    return runtime / f"ai-engineering-local-agent-{key}.lock"


def test_implementer_blocks_master(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, branch="master")
    head = _git(repo, "rev-parse", "HEAD")
    result = _run(repo, tmp_path, "implementer", "--expected-head", head, "--", "x")
    assert result.returncode == 3
    assert "implementer may not run on master" in result.stderr


def test_implementer_blocks_wrong_head(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    result = _run(
        repo,
        tmp_path,
        "implementer",
        "--expected-head",
        "0" * 40,
        "--",
        "x",
    )
    assert result.returncode == 3
    assert "expected HEAD does not match" in result.stderr


def test_implementer_blocks_dirty_worktree(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    result = _run(repo, tmp_path, "implementer", "--expected-head", head, "--", "x")
    assert result.returncode == 3
    assert "requires a clean worktree" in result.stderr


def test_implementer_blocks_when_writer_lock_is_owned(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD")
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    lock_path = _lock_path(repo, runtime)
    with lock_path.open("w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = _run(
            repo,
            tmp_path,
            "implementer",
            "--expected-head",
            head,
            "--",
            "x",
        )
    assert result.returncode == 3
    assert "another writer owns this worktree" in result.stderr


def test_implementer_fails_if_agent_changes_head(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD")
    result = _run(
        repo,
        tmp_path,
        "implementer",
        "--expected-head",
        head,
        "--",
        "x",
        fake_body='git commit --allow-empty -m "agent mutation" >/dev/null',
    )
    assert result.returncode == 4
    assert "implementer changed Git HEAD" in result.stderr


@pytest.mark.parametrize("role", ["repo-reader", "verifier"])
def test_read_only_role_fails_on_repository_mutation(
    tmp_path: Path,
    role: str,
) -> None:
    repo = _make_repo(tmp_path)
    before = _git(repo, "rev-parse", "HEAD")
    result = _run(
        repo,
        tmp_path,
        role,
        "--",
        "x",
        fake_body="touch MUTATED_BY_AGENT",
    )
    assert result.returncode == 4
    assert "read-only agent changed repository state" in result.stderr
    assert _git(repo, "rev-parse", "HEAD") == before


def test_verifier_blocks_while_writer_lock_is_owned(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    lock_path = _lock_path(repo, runtime)
    with lock_path.open("w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = _run(repo, tmp_path, "verifier", "--", "x")
    assert result.returncode == 3
    assert "writer is active in this worktree" in result.stderr


def test_verifier_holds_lock_for_entire_agent_run(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    lock_path = _lock_path(repo, runtime)
    result = _run(
        repo,
        tmp_path,
        "verifier",
        "--",
        "x",
        fake_body=(
            'if flock -n "$LOCK_PROBE_PATH" -c true; then '
            'echo "lock unexpectedly free" >&2; exit 9; fi'
        ),
        extra_env={"LOCK_PROBE_PATH": str(lock_path)},
    )
    assert result.returncode == 0


def test_read_only_role_passes_without_mutation(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    before_status = _git(repo, "status", "--porcelain=v1")
    result = _run(repo, tmp_path, "repo-reader", "--", "x")
    assert result.returncode == 0
    assert _git(repo, "status", "--porcelain=v1") == before_status
