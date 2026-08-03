"""
MCP STDIO server.
"""

from __future__ import annotations

import sys

from ..mcp import create_server
from ..runtime import MCPRuntime
from ..transport import MCPRequestHandler
from .codec import (
    decode_request,
    encode_response,
)


class STDIOTransportServer:
    """
    JSON over stdin/stdout MCP server.
    """

    def __init__(self) -> None:
        server = create_server()

        self._runtime = MCPRuntime(
            server.registry
        )

        self._handler = MCPRequestHandler(
            self._runtime
        )

    def process_line(
        self,
        line: str,
    ) -> str:
        """
        Process one JSON request.
        """

        request = decode_request(
            line
        )

        response = self._handler.handle(
            request
        )

        return encode_response(
            response
        )

    def run(self) -> None:
        """
        Start STDIO loop.
        """

        for line in sys.stdin:
            line = line.strip()

            if not line:
                continue

            output = self.process_line(
                line
            )

            print(
                output,
                flush=True,
            )