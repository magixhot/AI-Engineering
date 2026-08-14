"""
Built-in MCP tool metadata.
"""

from __future__ import annotations

from .models import (
    ToolMetadata,
    ToolParameter,
)

BUILTIN_TOOLS: tuple[ToolMetadata, ...] = (

    # ------------------------------------------------------------------
    # Workspace
    # ------------------------------------------------------------------

    ToolMetadata(
        name="workspace.list",
        description="List directory contents.",
        category="workspace",
    ),

    ToolMetadata(
        name="workspace.read_file",
        description="Read text file.",
        category="workspace",
        parameters=(
            ToolParameter(
                name="path",
                type="string",
                description="Path to file.",
            ),
        ),
    ),

    ToolMetadata(
        name="workspace.write_file",
        description="Write text file.",
        category="workspace",
    ),

    ToolMetadata(
        name="workspace.create_file",
        description="Create file.",
        category="workspace",
    ),

    ToolMetadata(
        name="workspace.create_directory",
        description="Create directory.",
        category="workspace",
    ),

    ToolMetadata(
        name="workspace.move",
        description="Move file or directory.",
        category="workspace",
    ),

    ToolMetadata(
        name="workspace.delete",
        description="Delete file or directory.",
        category="workspace",
    ),

    # ------------------------------------------------------------------
    # Git
    # ------------------------------------------------------------------

    ToolMetadata(
        name="git.status",
        description="Git status.",
        category="git",
    ),

    ToolMetadata(
        name="git.branch",
        description="Git branch.",
        category="git",
    ),

    ToolMetadata(
        name="git.log",
        description="Git log.",
        category="git",
    ),

    ToolMetadata(
        name="git.diff",
        description="Git diff.",
        category="git",
    ),

    # ------------------------------------------------------------------
    # Python
    # ------------------------------------------------------------------

    ToolMetadata(
        name="python.version",
        description="Python runtime version.",
        category="python",
    ),

    ToolMetadata(
        name="python.run_tests",
        description="Run pytest.",
        category="python",
    ),

    ToolMetadata(
        name="python.check_syntax",
        description="Validate Python syntax.",
        category="python",
    ),

    ToolMetadata(
        name="python.inspect_package",
        description="Inspect Python package.",
        category="python",
    ),
)
