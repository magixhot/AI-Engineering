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

    def __init__(self, repository: Path | None = None) -> None:
        self._repository = repository or Path.cwd()

    def _run(self, *args: str) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self._repository,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise GitCommandError(
                exc.stderr.strip()
            ) from exc
        except FileNotFoundError as exc:
            raise GitCommandError(
                "Git executable not found."
            ) from exc

        return result.stdout.strip()

    def status(self) -> GitStatus:
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

            if line[0] != " ":
                staged += 1

            if line[1] != " ":
                modified += 1

        return GitStatus(
            branch=branch,
            is_clean=not porcelain,
            staged=staged,
            modified=modified,
            untracked=untracked,
        )

    def branch(self) -> str:
        try:
            return self._run(
                "branch",
                "--show-current",
            )
        except GitCommandError as exc:
            raise GitRepositoryNotFoundError(
                "Current directory is not a Git repository."
            ) from exc

    def log(self, limit: int = 10) -> list[str]:
        output = self._run(
            "log",
            f"-{limit}",
            "--oneline",
        )

        return output.splitlines()

    def diff(self) -> str:
        return self._run("diff")