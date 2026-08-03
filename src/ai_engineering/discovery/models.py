"""
MCP Discovery models.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class ToolParameter:
    """
    Describes one MCP tool parameter.
    """

    name: str
    type: str
    required: bool = True
    description: str = ""


@dataclass(slots=True, frozen=True)
class ToolMetadata:
    """
    Metadata describing an MCP tool.
    """

    name: str
    description: str
    parameters: tuple[ToolParameter, ...] = ()
    category: str = "general"


@dataclass(slots=True)
class ServerMetadata:
    """
    Metadata describing the MCP server.
    """

    name: str
    version: str
    protocol_version: str = "1.0"
    tools: list[ToolMetadata] = field(
        default_factory=list
    )