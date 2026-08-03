"""
Unified Registry exceptions.
"""

from __future__ import annotations


class RegistryError(Exception):
    """
    Base registry exception.
    """


class ToolAlreadyRegisteredError(RegistryError):
    """
    Raised when attempting to register
    a tool that already exists.
    """


class ToolNotFoundError(RegistryError):
    """
    Raised when a requested tool
    cannot be found.
    """


class ToolDisabledError(RegistryError):
    """
    Raised when attempting to execute
    a disabled tool.
    """