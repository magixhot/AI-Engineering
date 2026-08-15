from __future__ import annotations

import json
import os
import subprocess
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import anyio
import pytest
from mcp.client.session import ClientSession
from mcp.types import CallToolResult, TextContent

from ai_engineering.git.exceptions import (
    GitPermissionError,
    GitRepositoryNotFoundError,
)
from ai_engineering.git.service import GitService
from ai_engineering.mcp.config import MCPConfig
from ai_engineering.mcp.sdk_adapter import SDKAdapter
from ai_engineering.mcp.server import create_server


def run_git(repository: Path, *args: str) -> str:
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_AUTHOR_NAME": "AI-Engineering Tests",
            "GIT_AUTHOR_EMAIL": "tests@example.invalid",
            "GIT_COMMITTER_NAME": "AI-Engineering Tests",
            "GIT_COMMITTER_EMAIL": "tests@example.invalid",
        }
    )
    result = subprocess.run(
        ["git", *args],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def initialize_repository(repository: Path) -> None:
    repository.mkdir(parents=True, exist_ok=True)
    run_git(repository, "init")
    (repository / "tracked.txt").write_text("initial", encoding="utf-8")
    run_git(repository, "add", "tracked.txt")
    run_git(repository, "commit", "-m", "initial commit")


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


def test_bounded_git_service_accepts_exact_repository_root(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    initialize_repository(repository)

    service = GitService(repository, bounded=True)

    status = service.status()
    assert status.is_clean is True
    assert service.branch() == run_git(repository, "branch", "--show-current")
    assert service.log()[0].endswith("initial commit")
    assert service.diff() == ""


def test_bounded_git_service_rejects_parent_repository_discovery(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    initialize_repository(repository)
    workspace = repository / "workspace"
    workspace.mkdir()

    service = GitService(workspace, bounded=True)

    with pytest.raises(
        GitPermissionError,
        match="outside the configured workspace root",
    ):
        service.status()


def test_bounded_git_service_rejects_non_repository_root(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    with pytest.raises(
        GitRepositoryNotFoundError,
        match="Workspace root is not a Git repository",
    ):
        GitService(workspace, bounded=True).branch()


@pytest.mark.anyio
async def test_active_mcp_git_status_uses_exact_workspace_repository_root(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    initialize_repository(repository)
    server = create_server(MCPConfig(workspace_root=repository))

    async with connected_session(server.sdk) as session:
        result = await session.call_tool("git_status", {})

    assert result.isError is False
    status = json.loads(result_text(result))
    assert status["is_clean"] is True
    assert status["staged"] == 0
    assert status["modified"] == 0
    assert status["untracked"] == 0


@pytest.mark.anyio
async def test_active_mcp_git_rejects_parent_repository_escape(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    initialize_repository(repository)
    workspace = repository / "workspace"
    workspace.mkdir()
    server = create_server(MCPConfig(workspace_root=workspace))

    async with connected_session(server.sdk) as session:
        result = await session.call_tool("git_status", {})

    assert result.isError is True
    assert result_text(result).startswith(
        "Error executing tool: Git repository root is outside the configured workspace root."
    )
