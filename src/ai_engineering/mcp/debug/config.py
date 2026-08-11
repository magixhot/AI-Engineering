"""
MCP Diagnostics configuration.
"""

import os
from pathlib import Path


def is_debug_enabled() -> bool:
    """
    Check if MCP debug mode is enabled.
    """
    return os.environ.get("AI_ENGINEERING_DEBUG_MCP") == "1"

def get_logs_dir() -> Path:
    """
    Ensure the logs directory exists and return its path.
    """
    log_dir = Path("logs")
    if is_debug_enabled():
        log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
