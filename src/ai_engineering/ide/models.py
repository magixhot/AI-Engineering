"""
IDE domain models.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IDEType(str, Enum):
    """
    Supported IDE types.
    """

    ANTIGRAVITY = "antigravity"
    VSCODE = "vscode"


class IDESessionStatus(str, Enum):
    """
    IDE session states.
    """

    CREATED = "created"
    CONNECTED = "connected"
    CLOSED = "closed"


@dataclass(slots=True, frozen=True)
class IDEProject:
    """
    Project opened in an IDE.
    """

    name: str
    path: str


@dataclass(slots=True, frozen=True)
class IDESession:
    """
    IDE connection session.
    """

    id: str
    ide: IDEType
    status: IDESessionStatus
    project: IDEProject | None = None