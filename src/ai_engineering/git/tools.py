"""Git MCP tools."""

from __future__ import annotations

from .service import GitService


class GitTools:
    """Adapt a specific GitService instance to MCP tool result shapes."""

    def __init__(self, service: GitService) -> None:
        self._service = service

    def status(self) -> dict:
        status = self._service.status()
        return {
            "branch": status.branch,
            "is_clean": status.is_clean,
            "staged": status.staged,
            "modified": status.modified,
            "untracked": status.untracked,
        }

    def branch(self) -> dict:
        return {
            "branch": self._service.branch(),
        }

    def log(self, limit: int = 10) -> dict:
        return {
            "commits": self._service.log(limit),
        }

    def diff(self) -> dict:
        return {
            "diff": self._service.diff(),
        }


_service = GitService()
_tools = GitTools(_service)


def git_status() -> dict:
    """Return Git repository status."""
    return _tools.status()


def git_branch() -> dict:
    """Return current Git branch."""
    return _tools.branch()


def git_log(limit: int = 10) -> dict:
    """Return recent Git commits."""
    return _tools.log(limit)


def git_diff() -> dict:
    """Return current Git diff."""
    return _tools.diff()
