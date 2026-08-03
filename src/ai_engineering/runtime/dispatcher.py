"""
MCP runtime tool dispatcher.
"""

from __future__ import annotations

from typing import Any

from ..mcp.registry import ToolRegistry
from .context import RuntimeContext
from .events import (
    RuntimeEvent,
    RuntimeEventType,
    create_event,
)


class ToolDispatcher:
    """
    Dispatches MCP tool calls through the registry.
    """

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        self._registry = registry
        self._events: list[RuntimeEvent] = []

    def dispatch(
        self,
        tool: str,
        context: RuntimeContext,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute registered tool.
        """

        self._events.append(
            create_event(
                RuntimeEventType.TOOL_CALLED,
                tool,
            )
        )

        try:
            result = self._registry.call(
                tool,
                *args,
                **kwargs,
            )

        except Exception as exc:
            self._events.append(
                create_event(
                    RuntimeEventType.TOOL_FAILED,
                    str(exc),
                )
            )

            raise

        self._events.append(
            create_event(
                RuntimeEventType.TOOL_COMPLETED,
                tool,
            )
        )

        return result

    def events(self) -> list[RuntimeEvent]:
        """
        Return runtime events.
        """

        return list(self._events)