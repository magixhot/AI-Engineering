"""
Workspace MCP tools.
"""

from __future__ import annotations

from pathlib import Path

from .service import WorkspaceService


class WorkspaceTools:
    """Workspace tool handlers bound to one WorkspaceService instance."""

    def __init__(self, service: WorkspaceService) -> None:
        self._service = service

    def list(self, path: str) -> list[dict]:
        entries = self._service.list_directory(Path(path))
        return [
            {
                "path": str(entry.path),
                "is_file": entry.is_file,
                "is_directory": entry.is_directory,
                "size": entry.size,
            }
            for entry in entries
        ]

    def read_file(self, path: str) -> dict:
        return {
            "path": path,
            "content": self._service.read_file(Path(path)),
        }

    def write_file(self, path: str, content: str) -> dict:
        self._service.write_file(Path(path), content)
        return {"success": True, "path": path}

    def create_file(self, path: str) -> dict:
        self._service.create_file(Path(path))
        return {"success": True, "path": path}

    def create_directory(self, path: str) -> dict:
        self._service.create_directory(Path(path))
        return {"success": True, "path": path}

    def move(self, source: str, destination: str) -> dict:
        self._service.move(Path(source), Path(destination))
        return {
            "success": True,
            "source": source,
            "destination": destination,
        }

    def delete(self, path: str) -> dict:
        self._service.delete(Path(path))
        return {"success": True, "path": path}


# Backward-compatible module-level Workspace tools are also bounded to the cwd
# captured when this module is imported. The active MCP server uses its own
# explicitly configured service instance instead.
_service = WorkspaceService(Path.cwd())
_tools = WorkspaceTools(_service)


def workspace_list(path: str) -> list[dict]:
    return _tools.list(path)


def workspace_read_file(path: str) -> dict:
    return _tools.read_file(path)


def workspace_write_file(path: str, content: str) -> dict:
    return _tools.write_file(path, content)


def workspace_create_file(path: str) -> dict:
    return _tools.create_file(path)


def workspace_create_directory(path: str) -> dict:
    return _tools.create_directory(path)


def workspace_move(source: str, destination: str) -> dict:
    return _tools.move(source, destination)


def workspace_delete(path: str) -> dict:
    return _tools.delete(path)
