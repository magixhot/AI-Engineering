"""
MCP Discovery registry.
"""

from __future__ import annotations

from .models import (
    ServerMetadata,
    ToolMetadata,
)


class DiscoveryRegistry:
    """
    Registry of MCP tool metadata.
    """

    def __init__(
        self,
        server_name: str = "AI-Engineering MCP",
        version: str = "0.1.0",
    ) -> None:
        self._server = ServerMetadata(
            name=server_name,
            version=version,
        )

    def register(
        self,
        tool: ToolMetadata,
    ) -> None:
        """
        Register tool metadata.
        """

        self._server.tools.append(tool)

    def tools(self) -> list[ToolMetadata]:
        """
        Return registered tools.
        """

        return list(self._server.tools)

    def server(self) -> ServerMetadata:
        """
        Return server metadata.
        """

        return self._server

    def find(
        self,
        name: str,
    ) -> ToolMetadata | None:
        """
        Find tool by name.
        """

        for tool in self._server.tools:
            if tool.name == name:
                return tool

        return None