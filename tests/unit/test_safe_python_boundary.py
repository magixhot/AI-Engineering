from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import anyio
import pytest
from mcp.client.session import ClientSession
from mcp.types import CallToolResult, TextContent

from ai_engineering.mcp.config import MCPConfig
from ai_engineering.mcp.sdk_adapter import SDKAdapter
from ai_engineering.mcp.server import create_server
from ai_engineering.python.exceptions import (
    PythonExecutionError,
    PythonPermissionError,
)
from ai_engineering.python.service import PythonService


def result_text(result: CallToolResult) -> str:
    content = result.content[0]
    assert isinstance(content, TextContent)
    return content.text


@asynccontextmanager
async def connected_session(adapter: SDKAdapter) -> AsyncIterator[ClientSession]:
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


def test_bounded_python_syntax_accepts_relative_and_absolute_in_root(
    tmp_path: Path,
) -> None:
    source = tmp_path / "package" / "module.py"
    source.parent.mkdir()
    source.write_text("value = 1\n", encoding="utf-8")
    service = PythonService(tmp_path, bounded=True)

    relative = service.check_syntax(Path("package/module.py"))
    absolute = service.check_syntax(source)

    assert relative.valid is True
    assert absolute.valid is True


def test_bounded_python_rejects_outside_syntax_and_package_paths(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside_file = tmp_path / "outside.py"
    outside_file.write_text("secret = True\n", encoding="utf-8")
    outside_package = tmp_path / "outside_package"
    outside_package.mkdir()
    service = PythonService(workspace, bounded=True)

    with pytest.raises(PythonPermissionError, match="outside configured workspace"):
        service.check_syntax(outside_file)
    with pytest.raises(PythonPermissionError, match="outside configured workspace"):
        service.inspect_package(outside_package)
    with pytest.raises(PythonPermissionError, match="outside configured workspace"):
        service.run_tests(Path("../outside.py"))


def test_bounded_python_package_inspection_succeeds_in_root(tmp_path: Path) -> None:
    package = tmp_path / "src" / "sample"
    package.mkdir(parents=True)
    (package / "b.py").write_text("", encoding="utf-8")
    (package / "a.py").write_text("", encoding="utf-8")

    service = PythonService(tmp_path, bounded=True)

    assert service.inspect_package(Path("src/sample")) == ["a.py", "b.py"]


def test_bounded_run_tests_uses_workspace_cwd_and_safe_subprocess(
    tmp_path: Path,
) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    result = MagicMock(returncode=0, stdout="ok", stderr="")
    service = PythonService(tmp_path, bounded=True, timeout=17)

    with patch("subprocess.run", return_value=result) as run:
        response = service.run_tests()

    assert response.success is True
    run.assert_called_once_with(
        [sys.executable, "-m", "pytest", str(tests.resolve())],
        cwd=tmp_path.resolve(),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        shell=False,
        timeout=17,
    )


def test_bounded_run_tests_timeout_is_controlled(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    service = PythonService(tmp_path, bounded=True, timeout=1)

    with patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="pytest", timeout=1),
    ):
        with pytest.raises(PythonExecutionError, match="timed out"):
            service.run_tests()


@pytest.mark.anyio
async def test_active_mcp_python_operations_use_workspace_root(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text("value = 1\n", encoding="utf-8")
    package = tmp_path / "package"
    package.mkdir()
    (package / "alpha.py").write_text("", encoding="utf-8")
    server = create_server(MCPConfig(workspace_root=tmp_path))

    async with connected_session(server.sdk) as session:
        syntax = await session.call_tool(
            "python_check_syntax",
            {"file": "module.py"},
        )
        inspected = await session.call_tool(
            "python_inspect_package",
            {"path": "package"},
        )
        version = await session.call_tool("python_version", {})

    assert syntax.isError is False
    assert json.loads(result_text(syntax))["valid"] is True
    assert inspected.isError is False
    assert json.loads(result_text(inspected))["modules"] == ["alpha.py"]
    assert version.isError is False


@pytest.mark.anyio
async def test_active_mcp_python_rejects_outside_paths(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("secret = True\n", encoding="utf-8")
    server = create_server(MCPConfig(workspace_root=workspace))

    async with connected_session(server.sdk) as session:
        syntax = await session.call_tool(
            "python_check_syntax",
            {"file": str(outside)},
        )
        tests = await session.call_tool(
            "python_run_tests",
            {"path": str(outside)},
        )

    assert syntax.isError is True
    assert result_text(syntax).startswith(
        "Error executing tool: Path outside configured workspace root."
    )
    assert tests.isError is True
    assert result_text(tests).startswith(
        "Error executing tool: Path outside configured workspace root."
    )
