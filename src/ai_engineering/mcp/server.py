"""
AI-Engineering MCP Server.
"""

from __future__ import annotations

from ..git import git_branch, git_diff, git_log, git_status
from ..python import (
    python_check_syntax,
    python_inspect_package,
    python_run_tests,
    python_version,
)
from ..registry.composite import CompositeRegistry
from ..workspace import WorkspaceService, WorkspaceTools
from .config import MCPConfig
from .lifecycle import MCPLifecycle
from .sdk_adapter import SDKAdapter


class EngineeringMCPServer:
    """Coordinate server lifecycle and registered MCP tools."""

    def __init__(self, config: MCPConfig | None = None) -> None:
        self._config = config or MCPConfig()
        self._registry = CompositeRegistry()
        self._lifecycle = MCPLifecycle(self._config)
        self._workspace_service = WorkspaceService(self._config.workspace_root)
        self._workspace_tools = WorkspaceTools(self._workspace_service)

        self._register_builtin_tools()
        self._sdk = SDKAdapter(self._registry)

    def _register_builtin_tools(self) -> None:
        self._registry.register(
            name="workspace.list",
            handler=self._workspace_tools.list,
            description="List workspace directory.",
            category="workspace",
        )
        self._registry.register(
            name="workspace.read_file",
            handler=self._workspace_tools.read_file,
            description="Read text file.",
            category="workspace",
        )
        self._registry.register(
            name="workspace.write_file",
            handler=self._workspace_tools.write_file,
            description="Write text file.",
            category="workspace",
        )
        self._registry.register(
            name="workspace.create_file",
            handler=self._workspace_tools.create_file,
            description="Create file.",
            category="workspace",
        )
        self._registry.register(
            name="workspace.create_directory",
            handler=self._workspace_tools.create_directory,
            description="Create directory.",
            category="workspace",
        )
        self._registry.register(
            name="workspace.move",
            handler=self._workspace_tools.move,
            description="Move file or directory.",
            category="workspace",
        )
        self._registry.register(
            name="workspace.delete",
            handler=self._workspace_tools.delete,
            description="Delete file or directory.",
            category="workspace",
        )

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
        self._lifecycle.stop()

    @property
    def sdk(self) -> SDKAdapter:
        return self._sdk


def create_server(config: MCPConfig | None = None) -> EngineeringMCPServer:
    """Create an Engineering MCP server."""

    return EngineeringMCPServer(config)
