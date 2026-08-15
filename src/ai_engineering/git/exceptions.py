"""Git exceptions."""

from __future__ import annotations


class GitError(Exception):
    """Base exception for Git operations."""


class GitRepositoryNotFoundError(GitError):
    """Raised when the configured directory is not a Git repository."""


class GitPermissionError(GitError):
    """Raised when an MCP Git operation would escape its authority root."""


class GitCommandError(GitError):
    """Raised when a Git command fails."""
