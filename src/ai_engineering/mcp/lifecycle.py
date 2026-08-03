"""
AI-Engineering MCP

Lifecycle
"""

from __future__ import annotations

import logging

from .config import MCPConfig

logger = logging.getLogger(__name__)


class MCPLifecycle:
    """
    Controls the lifecycle of the Engineering MCP server.
    """

    def __init__(self, config: MCPConfig) -> None:
        self._config = config
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            logger.warning("MCP server is already running.")
            return

        logger.info(
            "Starting %s %s",
            self._config.server_name,
            self._config.server_version,
        )

        self._running = True

    def stop(self) -> None:
        if not self._running:
            logger.warning("MCP server is not running.")
            return

        logger.info("Stopping MCP server.")

        self._running = False