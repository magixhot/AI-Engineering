# Файл:
# src/ai_engineering/git/exceptions.py

"""
Git exceptions.
"""

from __future__ import annotations


class GitError(Exception):
    """Base exception for Git operations."""


class GitRepositoryNotFoundError(GitError):
    """Raised when the current directory is not a Git repository."""


class GitCommandError(GitError):
    """Raised when a Git command fails."""