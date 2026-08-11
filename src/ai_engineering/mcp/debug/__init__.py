"""
MCP Diagnostics Module.

Provides minimally invasive debugging, wire tracing, and runtime
logging for the MCP infrastructure.
"""

from .config import get_logs_dir, is_debug_enabled
from .logger import get_runtime_logger
from .streams import wrap_stdio

__all__ = [
    "is_debug_enabled",
    "get_logs_dir",
    "get_runtime_logger",
    "wrap_stdio",
]
