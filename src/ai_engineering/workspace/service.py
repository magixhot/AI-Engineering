"""
Workspace service.
"""

from __future__ import annotations

from pathlib import Path

from .exceptions import (
    WorkspaceAlreadyExistsError,
    WorkspaceNotFoundError,
)
from .models import WorkspaceEntry


class WorkspaceService:
    """
    Provides filesystem operations for the Engineering MCP.
    """

    def list_directory(self, path: Path) -> list[WorkspaceEntry]:
        if not path.exists():
            raise WorkspaceNotFoundError(f"Directory not found: {path}")

        if not path.is_dir():
            raise WorkspaceNotFoundError(f"Not a directory: {path}")

        entries: list[WorkspaceEntry] = []

        for item in sorted(path.iterdir()):
            entries.append(
                WorkspaceEntry(
                    path=item,
                    is_file=item.is_file(),
                    is_directory=item.is_dir(),
                    size=item.stat().st_size if item.is_file() else 0,
                )
            )

        return entries

    def read_file(self, path: Path, encoding: str = "utf-8") -> str:
        if not path.exists():
            raise WorkspaceNotFoundError(f"File not found: {path}")

        return path.read_text(encoding=encoding)

    def write_file(
        self,
        path: Path,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        path.write_text(content, encoding=encoding)

    def create_file(self, path: Path) -> None:
        if path.exists():
            raise WorkspaceAlreadyExistsError(f"File already exists: {path}")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    def create_directory(self, path: Path) -> None:
        if path.exists():
            raise WorkspaceAlreadyExistsError(
                f"Directory already exists: {path}"
            )

        path.mkdir(parents=True)

    def move(self, source: Path, destination: Path) -> None:
        if not source.exists():
            raise WorkspaceNotFoundError(f"Source not found: {source}")

        source.rename(destination)

    def delete(self, path: Path) -> None:
        if not path.exists():
            raise WorkspaceNotFoundError(f"Path not found: {path}")

        if path.is_file():
            path.unlink()
        else:
            path.rmdir()