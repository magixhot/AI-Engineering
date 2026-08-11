"""
Official MCP SDK bootstrap.
"""

from __future__ import annotations

import anyio
from mcp.server.stdio import stdio_server

from .server import create_server


async def run() -> None:
    """
    Run the official MCP SDK server.
    """

    engineering = create_server()

    async with stdio_server() as (
        read_stream,
        write_stream,
    ):
        await engineering.sdk.server.run(
            read_stream,
            write_stream,
            engineering.sdk.server.create_initialization_options(),
        )


def main() -> None:
    """
    Entry point.
    """

    anyio.run(run)