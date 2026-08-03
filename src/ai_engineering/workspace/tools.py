# Файл:
# src/ai_engineering/workspace/tools.py

"""
Workspace MCP tools.
"""

from __future__ import annotations

from pathlib import Path

from .service import WorkspaceService

_service = WorkspaceService()


def workspace_list(path: str) -> list[dict]:
    entries = _service.list_directory(Path(path))

    return [
        {
            "path": str(entry.path),
            "is_file": entry.is_file,
            "is_directory": entry.is_directory,
            "size": entry.size,
        }
        for entry in entries
    ]


def workspace_read_file(path: str) -> dict:
    return {
        "path": path,
        "content": _service.read_file(Path(path)),
    }


def workspace_write_file(path: str, content: str) -> dict:
    _service.write_file(Path(path), content)

    return {
        "success": True,
        "path": path,
    }


def workspace_create_file(path: str) -> dict:
    _service.create_file(Path(path))

    return {
        "success": True,
        "path": path,
    }


def workspace_create_directory(path: str) -> dict:
    _service.create_directory(Path(path))

    return {
        "success": True,
        "path": path,
    }


def workspace_move(source: str, destination: str) -> dict:
    _service.move(Path(source), Path(destination))

    return {
        "success": True,
        "source": source,
        "destination": destination,
    }


def workspace_delete(path: str) -> dict:
    _service.delete(Path(path))

    return {
        "success": True,
        "path": path,
    }