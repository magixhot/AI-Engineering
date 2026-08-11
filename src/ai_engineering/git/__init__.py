"""
Git package.
"""

from .exceptions import (
    GitCommandError,
    GitError,
    GitRepositoryNotFoundError,
)
from .models import GitStatus
from .service import GitService
from .tools import (
    git_branch,
    git_diff,
    git_log,
    git_status,
)

__all__ = [

    # Exceptions
    "GitError",
    "GitCommandError",
    "GitRepositoryNotFoundError",

    # Models
    "GitStatus",

    # Service
    "GitService",

    # MCP tools
    "git_status",
    "git_branch",
    "git_log",
    "git_diff",
]