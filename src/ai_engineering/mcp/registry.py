"""
AI-Engineering MCP

Tool Registry
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

ToolHandler = Callable[..., Any]


class ToolRegistry:
    """
    Legacy executable tool registry.
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolHandler] = {}

    def register(
        self,
        name: str,
        handler: ToolHandler,
    ) -> None:
        if name in self._tools:
            raise ValueError(
                f"Tool '{name}' is already registered."
            )

        self._tools[name] = handler

    def unregister(
        self,
        name: str,
    ) -> None:
        self._tools.pop(name, None)

    def get(
        self,
        name: str,
    ) -> ToolHandler:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(
                f"Unknown tool: {name}"
            ) from exc

    def exists(
        self,
        name: str,
    ) -> bool:
        return name in self._tools

    def names(self) -> list[str]:
        return sorted(self._tools.keys())

    def call(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return self.get(name)(
            *args,
            **kwargs,
        )

    def clear(self) -> None:
        self._tools.clear()