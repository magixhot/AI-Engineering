"""
Python development exceptions.
"""

from __future__ import annotations


class PythonToolError(Exception):
    """
    Base exception for Python tools.
    """


class PythonExecutionError(PythonToolError):
    """
    Raised when a Python command execution fails.
    """


class PythonPermissionError(PythonToolError):
    """Raised when a Python operation escapes the configured workspace root."""


class SyntaxValidationError(PythonToolError):
    """
    Raised when syntax validation cannot be completed.
    """