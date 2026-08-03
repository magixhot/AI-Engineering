"""
Unified Tool Descriptor.

Single canonical description of an MCP tool.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ..discovery.models import ToolParameter


@dataclass(slots=True)
class ToolDescriptor:
    """
    Canonical description of one MCP tool.
    """

    name: str

    handler: Callable[..., Any]

    description: str

    category: str = "general"

    parameters: tuple[ToolParameter, ...] = ()

    version: str = "1.0.0"

    enabled: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def disable(self) -> None:
        """
        Disable tool.
        """

        self.enabled = False

    def enable(self) -> None:
        """
        Enable tool.
        """

        self.enabled = True