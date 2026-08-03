# Файл:
# src/ai_engineering/tests/unit/test_workspace_tools.py

from ai_engineering.mcp import create_server


def test_workspace_tools_are_registered() -> None:
    server = create_server()

    assert server.registry.exists("workspace.list")
    assert server.registry.exists("workspace.read_file")