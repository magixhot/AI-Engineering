"""
Workspace exceptions.
"""

from __future__ import annotations


class WorkspaceError(Exception):
    """Base exception for workspace operations."""


class WorkspaceNotFoundError(WorkspaceError):
    """Raised when a filesystem object cannot be found."""


class WorkspacePermissionError(WorkspaceError):
    """Raised when an operation is not permitted."""


class WorkspaceAlreadyExistsError(WorkspaceError):
    """Raised when attempting to create an existing object."""