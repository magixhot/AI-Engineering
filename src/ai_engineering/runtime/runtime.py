"""
MCP Runtime core.
"""

from __future__ import annotations

from typing import Any

from ..mcp.registry import ToolRegistry
from .context import RuntimeContext
from .dispatcher import ToolDispatcher
from .events import (
    RuntimeEvent,
    RuntimeEventType,
    create_event,
)


class MCPRuntime:
    """
    Main execution runtime for MCP tools.
    """

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        self._context = RuntimeContext()
        self._dispatcher = ToolDispatcher(
            registry
        )

        self._events: list[RuntimeEvent] = [
            create_event(
                RuntimeEventType.STARTED,
                "MCP Runtime started",
            )
        ]

    @property
    def context(self) -> RuntimeContext:
        return self._context

    def call(
        self,
        tool: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute MCP tool.
        """

        return self._dispatcher.dispatch(
            tool,
            self._context,
            *args,
            **kwargs,
        )

    def events(self) -> list[RuntimeEvent]:
        """
        Return runtime events.
        """

        return [
            *self._events,
            *self._dispatcher.events(),
        ]

    def stop(self) -> None:
        """
        Stop runtime.
        """

        self._events.append(
            create_event(
                RuntimeEventType.STOPPED,
                "MCP Runtime stopped",
            )
        )