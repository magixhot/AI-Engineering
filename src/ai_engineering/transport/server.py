"""
MCP transport server.
"""

from __future__ import annotations

from ..runtime import MCPRuntime
from .handlers import MCPRequestHandler
from .messages import (
    MCPRequest,
    MCPResponse,
)
from .protocol import MCPTransportProtocol


class MCPServerTransport:
    """
    Minimal MCP server transport.

    Provides request processing layer.
    Real network transport will be added later.
    """

    def __init__(
        self,
        runtime: MCPRuntime,
        transport: MCPTransportProtocol,
    ) -> None:
        self._runtime = runtime
        self._handler = MCPRequestHandler(
            runtime
        )
        self._transport = transport

    def process(
        self,
        request: MCPRequest,
    ) -> MCPResponse:
        """
        Process single MCP request.
        """

        return self._handler.handle(
            request
        )

    def serve_once(self) -> None:
        """
        Receive and process one request.
        """

        request = self._transport.receive()

        response = self.process(
            request
        )

        self._transport.send(
            response
        )

    def close(self) -> None:
        """
        Close transport.
        """

        self._transport.close()