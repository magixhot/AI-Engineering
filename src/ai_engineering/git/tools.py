"""
Git MCP tools.
"""

from __future__ import annotations

from .service import GitService

_service = GitService()


def git_status() -> dict:
    """
    Return Git repository status.
    """

    status = _service.status()

    return {
        "branch": status.branch,
        "is_clean": status.is_clean,
        "staged": status.staged,
        "modified": status.modified,
        "untracked": status.untracked,
    }


def git_branch() -> dict:
    """
    Return current Git branch.
    """

    return {
        "branch": _service.branch(),
    }


def git_log(limit: int = 10) -> dict:
    """
    Return recent Git commits.
    """

    return {
        "commits": _service.log(limit),
    }


def git_diff() -> dict:
    """
    Return current Git diff.
    """

    return {
        "diff": _service.diff(),
    }