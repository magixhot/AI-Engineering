# Файл:
# src/ai_engineering/workspace/models.py

"""
Workspace domain models.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class WorkspaceEntry:
    """
    Represents a filesystem entry.
    """

    path: Path
    is_file: bool
    is_directory: bool
    size: int = 0