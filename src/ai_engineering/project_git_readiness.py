"""Bounded read-only Git readiness observation for AUTO-0006."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class ProjectGitReadinessError(RuntimeError):
    """Raised when bounded Git readiness observation cannot complete safely."""


@dataclass(frozen=True)
class ProjectGitReadiness:
    """Immutable read-only Git state used by the AUTO-0006 health report."""

    repository: bool
    branch: str | None
    head: str | None
    staged_paths: tuple[str, ...]
    unstaged_paths: tuple[str, ...]
    untracked_paths: tuple[str, ...]

    @property
    def state(self) -> str:
        if not self.repository:
            return "not_repository"
        if self.head is None:
            return "repository_without_head"
        if self.branch is None:
            return "detached_or_unborn"
        if self.staged_paths or self.unstaged_paths or self.untracked_paths:
            return "ready_dirty"
        return "ready_clean"


def _run_git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            check=False,
            shell=False,
            stdin=subprocess.DEVNULL,
        )
    except OSError as exc:
        raise ProjectGitReadinessError(
            "Git readiness inspection could not start"
        ) from exc
    if result.returncode != 0:
        raise ProjectGitReadinessError(
            "Git readiness inspection failed for: " + " ".join(args)
        )
    return result.stdout


def _paths(output: str) -> tuple[str, ...]:
    return tuple(sorted(line for line in output.splitlines() if line))


def inspect_project_git_readiness(
    project_root: Path,
    *,
    repository: bool,
    branch: str | None,
    head: str | None,
) -> ProjectGitReadiness:
    """Observe bounded Git state without mutating repository metadata or files."""

    root = project_root.resolve()
    if not repository:
        return ProjectGitReadiness(False, branch, head, (), (), ())

    staged = _paths(_run_git(root, "diff", "--cached", "--name-only", "--"))
    unstaged = _paths(_run_git(root, "diff", "--name-only", "--"))
    untracked = _paths(
        _run_git(root, "ls-files", "--others", "--exclude-standard", "--")
    )
    return ProjectGitReadiness(
        repository=True,
        branch=branch,
        head=head,
        staged_paths=staged,
        unstaged_paths=unstaged,
        untracked_paths=untracked,
    )
