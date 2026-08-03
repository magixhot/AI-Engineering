"""
MCP transport messages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class MCPRequest:
    """
    Incoming MCP request.
    """

    id: str
    method: str
    params: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(slots=True, frozen=True)
class MCPResponse:
    """
    MCP response message.
    """

    id: str
    result: Any | None = None
    error: str | None = None


@dataclass(slots=True, frozen=True)
class MCPNotification:
    """
    MCP event notification.
    """

    method: str
    params: dict[str, Any] = field(
        default_factory=dict
    )