"""
Unit tests for GitService.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_engineering.git.exceptions import (
    GitCommandError,
    GitRepositoryNotFoundError,
)
from ai_engineering.git.service import GitService


def run_git(repository: Path, *args: str) -> str:
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_AUTHOR_NAME": "AI-Engineering Tests",
            "GIT_AUTHOR_EMAIL": "tests@example.invalid",
            "GIT_COMMITTER_NAME": "AI-Engineering Tests",
            "GIT_COMMITTER_EMAIL": "tests@example.invalid",
        }
    )
    result = subprocess.run(
        ["git", *args],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def initialize_repository(tmp_path: Path) -> Path:
    repository = tmp_path / "repository"
    repository.mkdir()
    run_git(repository, "init")
    (repository / "tracked.txt").write_text("initial", encoding="utf-8")
    run_git(repository, "add", "tracked.txt")
    run_git(repository, "commit", "-m", "initial commit")
    return repository


def test_status_reports_real_clean_modified_and_untracked_states(
    tmp_path: Path,
) -> None:
    repository = initialize_repository(tmp_path)
    service = GitService(repository)

    clean = service.status()
    assert clean.is_clean is True
    assert clean.staged == 0
    assert clean.modified == 0
    assert clean.untracked == 0

    (repository / "tracked.txt").write_text("changed", encoding="utf-8")
    modified = service.status()
    assert modified.is_clean is False
    assert modified.staged == 0
    assert modified.modified == 1
    assert modified.untracked == 0

    (repository / "untracked.txt").write_text("new", encoding="utf-8")
    untracked = service.status()
    assert untracked.modified == 1
    assert untracked.untracked == 1


def mocked_result(stdout: str = "") -> MagicMock:
    """
    Create a successful subprocess result mock.
    """
    result = MagicMock()
    result.stdout = stdout
    result.stderr = ""
    return result


def test_run_success(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    with patch("subprocess.run", return_value=mocked_result("ok")):
        result = service._run("status")

    assert result == "ok"


def test_run_preserves_porcelain_status_columns(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    with patch("subprocess.run", return_value=mocked_result(" M tracked.txt\n")):
        result = service._run("status", "--porcelain")

    assert result == " M tracked.txt"


def test_run_command_error(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["git", "status"],
        stderr="fatal error",
    )

    with patch("subprocess.run", side_effect=error):
        with pytest.raises(GitCommandError):
            service._run("status")


def test_run_git_not_found(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    with patch(
        "subprocess.run",
        side_effect=FileNotFoundError(),
    ):
        with pytest.raises(GitCommandError):
            service._run("status")


def test_branch(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    with patch.object(
        service,
        "_run",
        return_value="master",
    ):
        assert service.branch() == "master"


def test_branch_repository_not_found(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    with patch.object(
        service,
        "_run",
        side_effect=GitCommandError("not repository"),
    ):
        with pytest.raises(GitRepositoryNotFoundError):
            service.branch()


def test_log(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    with patch.object(
        service,
        "_run",
        return_value="abc123 first\ndef456 second",
    ):
        result = service.log(limit=2)

    assert result == [
        "abc123 first",
        "def456 second",
    ]


def test_diff(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    with patch.object(
        service,
        "_run",
        return_value="diff output",
    ):
        assert service.diff() == "diff output"


def test_status_clean_repository(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    with patch.object(
        service,
        "branch",
        return_value="master",
    ), patch.object(
        service,
        "_run",
        return_value="",
    ):
        result = service.status()

    assert result.branch == "master"
    assert result.is_clean is True
    assert result.staged == 0
    assert result.modified == 0
    assert result.untracked == 0


def test_status_mixed_changes(tmp_path: Path) -> None:
    service = GitService(tmp_path)

    porcelain = "\n".join(
        [
            "M  staged.txt",
            " M modified.txt",
            "?? new.txt",
        ]
    )

    with patch.object(
        service,
        "branch",
        return_value="master",
    ), patch.object(
        service,
        "_run",
        return_value=porcelain,
    ):
        result = service.status()

    assert result.branch == "master"
    assert result.is_clean is False
    assert result.staged == 1
    assert result.modified == 1
    assert result.untracked == 1