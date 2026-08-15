"""
MCP tool name mapper.
"""

from __future__ import annotations


class ToolNameMapper:
    """
    Maps between internal Engineering tool names
    and MCP-compatible tool names.
    """

    @staticmethod
    def to_mcp(
        name: str,
    ) -> str:
        """
        Convert internal name into MCP name.
        """

        return name.replace(".", "_")

    @staticmethod
    def from_mcp(
        name: str,
    ) -> str:
        """
        Convert MCP name into internal name.
        """

        return name.replace("_", ".", 1)
