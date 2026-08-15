from __future__ import annotations

from typing import Any

from ai_engineering.mcp.server import create_server

EXPECTED_TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "workspace_list": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    "workspace_read_file": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    "workspace_write_file": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["path", "content"],
    },
    "workspace_create_file": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    "workspace_create_directory": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    "workspace_move": {
        "type": "object",
        "properties": {
            "source": {"type": "string"},
            "destination": {"type": "string"},
        },
        "required": ["source", "destination"],
    },
    "workspace_delete": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    "git_status": {"type": "object", "properties": {}},
    "git_branch": {"type": "object", "properties": {}},
    "git_log": {
        "type": "object",
        "properties": {"limit": {"type": "integer", "default": 10}},
    },
    "git_diff": {"type": "object", "properties": {}},
    "python_version": {"type": "object", "properties": {}},
    "python_run_tests": {
        "type": "object",
        "properties": {"path": {"type": "string", "default": None}},
    },
    "python_check_syntax": {
        "type": "object",
        "properties": {"file": {"type": "string"}},
        "required": ["file"],
    },
    "python_inspect_package": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
}


def test_builtin_registry_exposes_all_canonical_and_mcp_names() -> None:
    descriptors = create_server().registry.descriptors()

    assert {descriptor.name for descriptor in descriptors} == {
        "workspace.list",
        "workspace.read_file",
        "workspace.write_file",
        "workspace.create_file",
        "workspace.create_directory",
        "workspace.move",
        "workspace.delete",
        "git.status",
        "git.branch",
        "git.log",
        "git.diff",
        "python.version",
        "python.run_tests",
        "python.check_syntax",
        "python.inspect_package",
    }
    assert {descriptor.mcp_name for descriptor in descriptors} == set(
        EXPECTED_TOOL_SCHEMAS
    )


def test_builtin_descriptors_produce_the_documented_input_schemas() -> None:
    descriptors = create_server().registry.descriptors()

    schemas = {
        descriptor.mcp_name: descriptor.to_mcp_tool().inputSchema
        for descriptor in descriptors
    }

    assert schemas == EXPECTED_TOOL_SCHEMAS
