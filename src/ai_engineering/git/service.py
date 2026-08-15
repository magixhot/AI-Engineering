"""
Git service.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .exceptions import (
    GitCommandError,
    GitRepositoryNotFoundError,
)
from .models import GitStatus


class GitService:
    """
    Provides Git operations for the Engineering MCP.
    """

    def __init__(
        self,
        repository: Path | None = None,
    ) -> None:
        self._repository = repository or Path.cwd()

    def _run(
        self,
        *args: str,
    ) -> str:
        """
        Execute Git command.
        """

        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self._repository,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )

        except subprocess.TimeoutExpired as exc:
            raise GitCommandError(
                "Git command timed out."
            ) from exc

        except subprocess.CalledProcessError as exc:
            raise GitCommandError(
                exc.stderr.strip()
            ) from exc

        except FileNotFoundError as exc:
            raise GitCommandError(
                "Git executable not found."
            ) from exc

        return result.stdout.rstrip("\r\n")

    def status(self) -> GitStatus:
        """
        Return repository status.
        """

        branch = self.branch()

        porcelain = self._run(
            "status",
            "--porcelain",
        )

        staged = 0
        modified = 0
        untracked = 0

        for line in porcelain.splitlines():
            if line.startswith("??"):
                untracked += 1
                continue

            if line and line[0] != " ":
                staged += 1

            if len(line) > 1 and line[1] != " ":
                modified += 1

        return GitStatus(
            branch=branch,
            is_clean=not porcelain,
            staged=staged,
            modified=modified,
            untracked=untracked,
        )

    def branch(self) -> str:
        """
        Return current branch.
        """

        try:
            return self._run(
                "branch",
                "--show-current",
            )

        except GitCommandError as exc:
            raise GitRepositoryNotFoundError(
                "Current directory is not a Git repository."
            ) from exc

    def log(
        self,
        limit: int = 10,
    ) -> list[str]:
        """
        Return commit log.
        """

        output = self._run(
            "log",
            f"-{limit}",
            "--oneline",
        )

        return output.splitlines()

    def diff(self) -> str:
        """
        Return Git diff.
        """

        return self._run("diff")
