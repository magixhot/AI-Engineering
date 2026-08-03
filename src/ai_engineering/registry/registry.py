"""
Unified Tool Registry.
"""

from __future__ import annotations

from typing import Any

from .descriptor import ToolDescriptor
from .exceptions import (
    ToolAlreadyRegisteredError,
    ToolDisabledError,
    ToolNotFoundError,
)


class UnifiedRegistry:
    """
    Unified registry for all MCP tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDescriptor] = {}

    def register(
        self,
        descriptor: ToolDescriptor,
    ) -> None:
        """
        Register a tool descriptor.
        """

        if descriptor.name in self._tools:
            raise ToolAlreadyRegisteredError(
                descriptor.name
            )

        self._tools[descriptor.name] = descriptor

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove tool from registry.
        """

        if name not in self._tools:
            raise ToolNotFoundError(name)

        del self._tools[name]

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check if tool exists.
        """

        return name in self._tools

    def descriptor(
        self,
        name: str,
    ) -> ToolDescriptor:
        """
        Return tool descriptor.
        """

        try:
            return self._tools[name]

        except KeyError as exc:
            raise ToolNotFoundError(name) from exc

    def call(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute registered tool.
        """

        descriptor = self.descriptor(name)

        if not descriptor.enabled:
            raise ToolDisabledError(name)

        return descriptor.handler(
            *args,
            **kwargs,
        )

    def descriptors(
        self,
    ) -> list[ToolDescriptor]:
        """
        Return all tool descriptors.
        """

        return list(self._tools.values())

    def names(
        self,
    ) -> list[str]:
        """
        Return tool names.
        """

        return sorted(self._tools.keys())