"""
AI-Engineering MCP

Server
"""

from __future__ import annotations

from ..git import (
    git_branch,
    git_diff,
    git_log,
    git_status,
)
from ..python import (
    python_check_syntax,
    python_inspect_package,
    python_run_tests,
    python_version,
)
from ..registry.composite import CompositeRegistry
from ..workspace import (
    workspace_create_directory,
    workspace_create_file,
    workspace_delete,
    workspace_list,
    workspace_move,
    workspace_read_file,
    workspace_write_file,
)
from .config import DEFAULT_CONFIG, MCPConfig
from .lifecycle import MCPLifecycle
from .sdk_adapter import SDKAdapter


class EngineeringMCPServer:
    """
    Engineering MCP Server.

    Coordinates the server lifecycle and manages the
    registry of available MCP tools.
    """

    def __init__(self, config: MCPConfig | None = None) -> None:
        self._config = config or DEFAULT_CONFIG
        self._registry = CompositeRegistry()
        self._lifecycle = MCPLifecycle(self._config)

        self._register_builtin_tools()

        # Official MCP SDK adapter
        self._sdk = SDKAdapter(
            self._registry
)

    def _register_builtin_tools(self) -> None:
        """
        Register built-in MCP tools.
        """

        # ------------------------------------------------------------------
        # Workspace
        # ------------------------------------------------------------------

        self._registry.register(
            name="workspace.list",
            handler=workspace_list,
            description="List workspace directory.",
            category="workspace",
        )

        self._registry.register(
            name="workspace.read_file",
            handler=workspace_read_file,
            description="Read text file.",
            category="workspace",
        )

        self._registry.register(
            name="workspace.write_file",
            handler=workspace_write_file,
            description="Write text file.",
            category="workspace",
        )

        self._registry.register(
            name="workspace.create_file",
            handler=workspace_create_file,
            description="Create file.",
            category="workspace",
        )

        self._registry.register(
            name="workspace.create_directory",
            handler=workspace_create_directory,
            description="Create directory.",
            category="workspace",
        )

        self._registry.register(
            name="workspace.move",
            handler=workspace_move,
            description="Move file or directory.",
            category="workspace",
        )

        self._registry.register(
            name="workspace.delete",
            handler=workspace_delete,
            description="Delete file or directory.",
            category="workspace",
        )

        # ------------------------------------------------------------------
        # Git
        # ------------------------------------------------------------------

        self._registry.register(
            name="git.status",
            handler=git_status,
            description="Git status.",
            category="git",
        )

        self._registry.register(
            name="git.branch",
            handler=git_branch,
            description="Git branch.",
            category="git",
        )

        self._registry.register(
            name="git.log",
            handler=git_log,
            description="Git commit log.",
            category="git",
        )

        self._registry.register(
            name="git.diff",
            handler=git_diff,
            description="Git diff.",
            category="git",
        )

        # ------------------------------------------------------------------
        # Python
        # ------------------------------------------------------------------

        self._registry.register(
            name="python.version",
            handler=python_version,
            description="Return Python version.",
            category="python",
        )

        self._registry.register(
            name="python.run_tests",
            handler=python_run_tests,
            description="Run pytest.",
            category="python",
        )

        self._registry.register(
            name="python.check_syntax",
            handler=python_check_syntax,
            description="Check Python syntax.",
            category="python",
        )

        self._registry.register(
            name="python.inspect_package",
            handler=python_inspect_package,
            description="Inspect Python package.",
            category="python",
        )

    @property
    def config(self) -> MCPConfig:
        return self._config

    @property
    def registry(self) -> CompositeRegistry:
        return self._registry

    @property
    def running(self) -> bool:
        return self._lifecycle.running

    def start(self) -> None:
        self._lifecycle.start()

    def stop(self) -> None:
        """
        Stop the MCP server.
        """

        self._lifecycle.stop()

    @property
    def sdk(self) -> SDKAdapter:
        """
        Return the official MCP SDK adapter.
        """

        return self._sdk


def create_server(
    config: MCPConfig | None = None,
) -> EngineeringMCPServer:
    """
    Factory for creating an Engineering MCP Server.
    """

    return EngineeringMCPServer(config)