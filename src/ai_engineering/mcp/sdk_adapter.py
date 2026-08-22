"""
Official Python MCP SDK adapter.
"""

from __future__ import annotations

import json
import logging
import time
import traceback
from typing import Any

from mcp.server import Server
from mcp.types import CallToolResult, TextContent

from ..registry.composite import CompositeRegistry
from .debug import get_runtime_logger
from .name_mapper import ToolNameMapper

logger = logging.getLogger(__name__)


class SDKAdapter:
    """
    Thin adapter between the official MCP SDK and
    the AI-Engineering Registry.
    """

    def __init__(
        self,
        registry: CompositeRegistry,
        *,
        version: str,
    ) -> None:

        self._registry = registry

        self._server = Server(
            name="AI-Engineering",
            version=version,
        )

        self._register_handlers()

    @property
    def server(self) -> Server:
        return self._server

    def _register_handlers(self) -> None:
        """
        Register SDK handlers.
        """

        @self._server.list_tools()
        async def list_tools():

            tools = [
                descriptor.to_mcp_tool()
                for descriptor in self._registry.descriptors()
            ]

            logger.debug(
                "Registered %d MCP tools.",
                len(tools),
            )

            return tools

        @self._server.call_tool()
        async def call_tool(
            name: str,
            arguments: dict[str, Any],
        ) -> list[TextContent] | CallToolResult:

            logger.debug(
                "Calling MCP tool: %s",
                name,
            )

            runtime_logger = get_runtime_logger()
            if runtime_logger:
                runtime_logger.info(f"Tool call: {name}")
                runtime_logger.debug(
                    "Arguments: "
                    f"{json.dumps(arguments, indent=2, default=str)}"
                )

            internal_name = ToolNameMapper.from_mcp(
                name,
            )

            start_time = time.monotonic()

            try:
                result = self._registry.call(
                    internal_name,
                    **(arguments or {}),
                )
            except Exception as e:
                elapsed = time.monotonic() - start_time
                logger.exception("Error executing tool %s", internal_name)
                if runtime_logger:
                    tb = traceback.format_exc()
                    runtime_logger.error(
                        f"Tool exception: {internal_name}"
                        f" ({elapsed * 1000:.1f} ms)\n{tb}"
                    )
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error executing tool: {e}",
                        )
                    ],
                    isError=True,
                )

            elapsed = time.monotonic() - start_time
            logger.debug(
                "Tool completed: %s",
                internal_name,
            )

            result_type = type(result).__name__

            if not isinstance(result, str):
                try:
                    text_result = json.dumps(result, indent=2, default=str)
                except Exception:
                    text_result = str(result)
            else:
                text_result = result

            if runtime_logger:
                size = len(text_result.encode("utf-8"))
                runtime_logger.info(
                    f"Tool result: {internal_name}"
                    f" ({elapsed * 1000:.1f} ms)"
                )
                runtime_logger.debug(
                    f"Returned type: {result_type}\n"
                    f"Returned class: {result.__class__.__name__}\n"
                    f"Serialized length: {size} bytes"
                )

            return [TextContent(type="text", text=text_result)]
