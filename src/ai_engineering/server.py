"""
Official AI-Engineering MCP Server.

Uses the official Python MCP SDK.
"""

from __future__ import annotations

from .mcp.sdk_adapter import SDKAdapter
from .registry.composite import CompositeRegistry


def create_server() -> SDKAdapter:
    """
    Create the official MCP server.
    """

    registry = CompositeRegistry()

    return SDKAdapter(
        registry,
    )