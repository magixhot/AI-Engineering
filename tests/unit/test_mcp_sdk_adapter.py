from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import anyio
import pytest
from mcp.client.session import ClientSession
from mcp.types import TextContent

from ai_engineering.mcp.name_mapper import ToolNameMapper
from ai_engineering.mcp.sdk_adapter import SDKAdapter
from ai_engineering.mcp.server import create_server
from ai_engineering.registry.composite import CompositeRegistry


@asynccontextmanager
async def connected_session(adapter: SDKAdapter) -> AsyncIterator[ClientSession]:
    """Run an SDK server and client session over public in-memory streams."""

    client_send: Any
    server_receive: Any
    client_send, server_receive = anyio.create_memory_object_stream(16)
    server_send: Any
    client_receive: Any
    server_send, client_receive = anyio.create_memory_object_stream(16)

    async with anyio.create_task_group() as task_group:
        task_group.start_soon(
            adapter.server.run,
            server_receive,
            server_send,
            adapter.server.create_initialization_options(),
        )
        async with ClientSession(client_receive, client_send) as session:
            await session.initialize()
            yield session
        task_group.cancel_scope.cancel()


def build_adapter(observed_calls: list[tuple[str, int]]) -> SDKAdapter:
    registry = CompositeRegistry()

    def echo(message: str, repeat: int = 1, enabled: bool = False) -> dict[str, Any]:
        return {
            "message": message * repeat,
            "enabled": enabled,
        }

    def fail(reason: str) -> str:
        raise RuntimeError(f"failure: {reason}")

    def record(value: str, count: int = 1) -> dict[str, int | str]:
        observed_calls.append((value, count))
        return {
            "value": value,
            "count": count,
        }

    registry.register(
        name="demo.echo",
        handler=echo,
        description="Return repeated input.",
    )
    registry.register(
        name="demo.fail",
        handler=fail,
        description="Raise a deterministic error.",
    )
    registry.register(
        name="demo.record",
        handler=record,
        description="Record dispatch arguments.",
    )
    return SDKAdapter(registry)


@pytest.mark.parametrize(
    ("internal_name", "mcp_name"),
    [
        ("workspace.read_file", "workspace_read_file"),
        ("python.check_syntax", "python_check_syntax"),
        ("workspace.list", "workspace_list"),
    ],
)
def test_tool_name_mapping_round_trips_snake_case_operations(
    internal_name: str,
    mcp_name: str,
) -> None:
    assert ToolNameMapper.to_mcp(internal_name) == mcp_name
    assert ToolNameMapper.from_mcp(mcp_name) == internal_name


@pytest.mark.anyio
async def test_list_tools_exposes_registered_mapped_names_and_schemas() -> None:
    adapter = build_adapter([])

    async with connected_session(adapter) as session:
        listed = await session.list_tools()

    tools = {tool.name: tool for tool in listed.tools}
    assert set(tools) == {"demo_echo", "demo_fail", "demo_record"}

    schema = tools["demo_echo"].inputSchema
    assert schema == {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "repeat": {"type": "integer", "default": 1},
            "enabled": {"type": "boolean", "default": False},
        },
        "required": ["message"],
    }


@pytest.mark.anyio
async def test_successful_mcp_call_maps_name_and_returns_text_content() -> None:
    adapter = build_adapter([])

    async with connected_session(adapter) as session:
        result = await session.call_tool(
            "demo_echo",
            {
                "message": "go",
                "repeat": 2,
                "enabled": True,
            },
        )

    assert result.isError is False
    assert result.content == [
        TextContent(
            type="text",
            text='''{
  "message": "gogo",
  "enabled": true
}''',
        )
    ]


@pytest.mark.anyio
async def test_mcp_call_dispatches_a_multiword_operation_name() -> None:
    registry = CompositeRegistry()
    observed_paths: list[str] = []

    def read_file(path: str) -> dict[str, str]:
        observed_paths.append(path)
        return {"path": path}

    registry.register(
        name="demo.read_file",
        handler=read_file,
        description="Record a file path.",
    )
    adapter = SDKAdapter(registry)

    async with connected_session(adapter) as session:
        listed = await session.list_tools()
        result = await session.call_tool("demo_read_file", {"path": "sample.txt"})

    assert [tool.name for tool in listed.tools] == ["demo_read_file"]
    assert result.isError is False
    assert observed_paths == ["sample.txt"]


@pytest.mark.anyio
async def test_workspace_read_file_returns_a_domain_error_for_a_missing_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    server = create_server()

    async with connected_session(server.sdk) as session:
        listed = await session.list_tools()
        result = await session.call_tool(
            "workspace_read_file",
            {"path": "MCP-0003-missing-file.txt"},
        )

    assert "workspace_read_file" in {tool.name for tool in listed.tools}
    assert result.isError is True
    error_content = result.content[0]
    assert isinstance(error_content, TextContent)
    assert error_content.text.startswith("Error executing tool: File not found:")
    assert "Unknown tool: workspace.read.file" not in error_content.text


@pytest.mark.anyio
async def test_composite_registry_dispatches_to_the_registered_handler() -> None:
    observed_calls: list[tuple[str, int]] = []
    adapter = build_adapter(observed_calls)

    async with connected_session(adapter) as session:
        result = await session.call_tool(
            "demo_record",
            {"value": "captured", "count": 3},
        )

    assert result.isError is False
    assert observed_calls == [("captured", 3)]


@pytest.mark.anyio
async def test_tool_execution_failure_returns_an_mcp_error_result() -> None:
    adapter = build_adapter([])

    async with connected_session(adapter) as session:
        result = await session.call_tool("demo_fail", {"reason": "expected"})

    assert result.isError is True
    assert result.content == [
        TextContent(type="text", text="Error executing tool: failure: expected")
    ]


@pytest.mark.anyio
async def test_unknown_tool_returns_a_deterministic_mcp_error_result() -> None:
    adapter = build_adapter([])

    async with connected_session(adapter) as session:
        result = await session.call_tool("demo_missing", {})

    assert result.isError is True
    assert result.content == [
        TextContent(
            type="text", text="Error executing tool: 'Unknown tool: demo.missing'"
        )
    ]


@pytest.mark.anyio
async def test_invalid_arguments_return_an_mcp_error_result() -> None:
    adapter = build_adapter([])

    async with connected_session(adapter) as session:
        result = await session.call_tool("demo_echo", {})

    assert result.isError is True
    assert result.content[0].type == "text"
    assert result.content[0].text.startswith("Input validation error:")
