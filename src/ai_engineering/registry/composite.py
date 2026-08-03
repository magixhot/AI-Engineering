"""
Composite Registry.

Coordinates legacy ToolRegistry and UnifiedRegistry.
"""

from __future__ import annotations

from typing import Any, Callable

from ..mcp.registry import ToolRegistry
from .descriptor import ToolDescriptor
from .registry import UnifiedRegistry


class CompositeRegistry:
    """
    Composite registry used during M3 migration.

    Keeps the legacy ToolRegistry and the new
    UnifiedRegistry synchronized.
    """

    def __init__(self) -> None:
        self._legacy = ToolRegistry()
        self._unified = UnifiedRegistry()

    @property
    def legacy(self) -> ToolRegistry:
        return self._legacy

    @property
    def unified(self) -> UnifiedRegistry:
        return self._unified

    def register(
        self,
        *,
        name: str,
        handler: Callable[..., Any],
        description: str = "",
        category: str = "general",
    ) -> None:
        """
        Register tool in both registries.
        """

        self._legacy.register(
            name,
            handler,
        )

        self._unified.register(
            ToolDescriptor(
                name=name,
                handler=handler,
                description=description,
                category=category,
            )
        )

    def call(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute tool through the legacy registry.
        """

        return self._legacy.call(
            name,
            *args,
            **kwargs,
        )

    def exists(
        self,
        name: str,
    ) -> bool:
        return self._legacy.exists(name)

    def names(self) -> list[str]:
        return self._legacy.names()