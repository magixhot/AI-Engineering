"""
Runtime logger for MCP Diagnostics.
Logs tool calls, arguments, timings, and exceptions.
"""

import logging

from .config import get_logs_dir, is_debug_enabled

_runtime_logger: logging.Logger | None = None

def get_runtime_logger() -> logging.Logger | None:
    """
    Get the runtime logger. Returns None if debug is disabled.
    """
    global _runtime_logger

    if not is_debug_enabled():
        return None

    if _runtime_logger is not None:
        return _runtime_logger

    logger = logging.getLogger("ai_engineering.mcp.diagnostics.runtime")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    log_file = get_logs_dir() / "mcp-runtime.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")

    # We use a standard format for runtime logs
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    _runtime_logger = logger
    return _runtime_logger
