"""
AI-Engineering MCP

Configuration
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class MCPConfig:
    """
    Global MCP configuration.
    """

    server_name: str = "ai-engineering"
    server_version: str = "0.2.0"

    workspace_root: Path = Path.cwd()

    enable_workspace_tools: bool = True
    enable_git_tools: bool = True
    enable_python_tools: bool = False

    log_level: str = "INFO"


DEFAULT_CONFIG = MCPConfig()
