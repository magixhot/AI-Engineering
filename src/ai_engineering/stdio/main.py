"""
MCP STDIO server entry point.
"""

from __future__ import annotations

from .server import STDIOTransportServer


def main() -> None:
    """
    Start MCP STDIO server.
    """

    server = STDIOTransportServer()

    server.run()


if __name__ == "__main__":
    main()