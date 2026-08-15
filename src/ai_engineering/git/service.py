"""Git service."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .exceptions import (
    GitCommandError,
    GitPermissionError,
    GitRepositoryNotFoundError,
)
from .models import GitStatus


class GitService:
    """Provide Git operations for AI-Engineering."""

    def __init__(
        self,
        repository: Path | None = None,
        *,
        bounded: bool = False,
    ) -> None:
        self._repository = (repository or Path.cwd()).resolve()
        self._bounded = bounded

    def _run(
        self,
        *args: str,
    ) -> str:
        """Execute a Git command in the configured repository directory."""

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

    def _authorize_repository(self) -> None:
        """Require the configured authority root to be the Git top-level directory."""
        if not self._bounded:
            return

        try:
            top_level = Path(
                self._run("rev-parse", "--show-toplevel")
            ).resolve()
        except GitCommandError as exc:
            raise GitRepositoryNotFoundError(
                "Workspace root is not a Git repository."
            ) from exc

        if top_level != self._repository:
            raise GitPermissionError(
                "Git repository root is outside the configured workspace root."
            )

    def status(self) -> GitStatus:
        """Return repository status."""
        self._authorize_repository()
        branch = self.branch(_authorized=True)

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

    def branch(self, *, _authorized: bool = False) -> str:
        """Return current branch."""
        if not _authorized:
            self._authorize_repository()

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
        """Return commit log."""
        self._authorize_repository()
        output = self._run(
            "log",
            f"-{limit}",
            "--oneline",
        )

        return output.splitlines()

    def diff(self) -> str:
        """Return Git diff."""
        self._authorize_repository()
        return self._run("diff")
