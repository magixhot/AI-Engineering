"""
MCP Discovery package.
"""

from .models import (
    ServerMetadata,
    ToolMetadata,
    ToolParameter,
)
from .registry import DiscoveryRegistry
from .tools import BUILTIN_TOOLS

__all__ = [
    "ToolParameter",
    "ToolMetadata",
    "ServerMetadata",
    "DiscoveryRegistry",
    "BUILTIN_TOOLS",
]