"""
Unified Tool Descriptor.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from types import UnionType
from typing import Any, Union, get_args, get_origin

from mcp.types import Tool

from ..mcp.name_mapper import ToolNameMapper


def _annotation_to_json_type(annotation: Any) -> str:
    """
    Convert a Python type annotation to a JSON Schema type string.
    """
    if annotation is inspect.Parameter.empty:
        return "string"

    # Resolve string annotations produced by `from __future__ import annotations`
    if isinstance(annotation, str):
        _MAP = {"int": "integer", "bool": "boolean", "float": "number"}
        base = annotation.split("|")[0].strip()
        return _MAP.get(base, "string")

    # Bare types
    if annotation is bool:
        return "boolean"
    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"

    # typing.Union / Optional  (e.g. Optional[int])
    origin = get_origin(annotation)
    if origin is Union:
        inner = get_args(annotation)
        if inner:
            return _annotation_to_json_type(inner[0])

    # PEP-604 union syntax  (e.g. int | None) — Python ≥ 3.10
    if isinstance(annotation, UnionType):
        inner = get_args(annotation)
        if inner:
            return _annotation_to_json_type(inner[0])

    return "string"


@dataclass(slots=True)
class ToolDescriptor:
    """
    Unified tool description.
    """

    name: str

    handler: Callable[..., Any]

    description: str = ""

    category: str = "general"

    enabled: bool = True

    @property
    def mcp_name(self) -> str:
        """
        Return MCP-compatible tool name.
        """

        return ToolNameMapper.to_mcp(
            self.name,
        )

    def to_mcp_tool(
        self,
    ) -> Tool:
        """
        Convert descriptor into the official MCP Tool.

        The inputSchema is derived from the handler's type annotations so
        MCP clients receive accurate parameter information.
        """
        sig = inspect.signature(self.handler)
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param_name, param in sig.parameters.items():
            json_type = _annotation_to_json_type(param.annotation)
            prop: dict[str, Any] = {"type": json_type}

            if param.default is not inspect.Parameter.empty:
                prop["default"] = param.default
            else:
                required.append(param_name)

            properties[param_name] = prop

        schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }
        if required:
            schema["required"] = required

        return Tool(
            name=self.mcp_name,
            description=self.description,
            inputSchema=schema,
        )