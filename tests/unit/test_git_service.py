"""
Unit tests for GitService.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_engineering.git.exceptions import (
    GitCommandError,
    GitRepositoryNotFoundError,
)
from ai_engineering.git.service import GitService


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