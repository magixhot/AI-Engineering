"""
MCP request handlers.
"""

from __future__ import annotations

from typing import Any

from ..runtime import MCPRuntime
from .messages import (
    MCPRequest,
    MCPResponse,
)


class MCPRequestHandler:
    """
    Handles incoming MCP requests.
    """

    def __init__(
        self,
        runtime: MCPRuntime,
    ) -> None:
        self._runtime = runtime

    def handle(
        self,
        request: MCPRequest,
    ) -> MCPResponse:
        """
        Execute MCP request.
        """

        try:
            result: Any = self._runtime.call(
                request.method,
                **request.params,
            )

            return MCPResponse(
                id=request.id,
                result=result,
            )

        except Exception as exc:
            return MCPResponse(
                id=request.id,
                error=str(exc),
            )