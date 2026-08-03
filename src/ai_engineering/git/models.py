# Файл:
# src/ai_engineering/git/models.py

"""
Git domain models.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GitStatus:
    """
    Represents the current Git repository status.
    """

    branch: str
    is_clean: bool
    staged: int
    modified: int
    untracked: int