"""
Python development domain models.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PythonVersion:
    """
    Python runtime information.
    """

    executable: str
    version: str


@dataclass(slots=True, frozen=True)
class TestResult:
    """
    Result of a test execution.
    """

    command: str
    success: bool
    exit_code: int
    output: str


@dataclass(slots=True, frozen=True)
class SyntaxCheckResult:
    """
    Python syntax validation result.
    """

    file: str
    valid: bool
    error: str | None = None