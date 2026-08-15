"""
Workspace service.
"""

from __future__ import annotations

from pathlib import Path

from .exceptions import (
    WorkspaceAlreadyExistsError,
    WorkspaceNotFoundError,
    WorkspacePermissionError,
)
from .models import WorkspaceEntry


class WorkspaceService:
    """Provide filesystem operations inside one configured workspace root."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        configured_root = workspace_root if workspace_root is not None else Path.cwd()
        try:
            resolved_root = configured_root.expanduser().resolve(strict=True)
        except FileNotFoundError as exc:
            raise WorkspaceNotFoundError(
                f"Workspace root not found: {configured_root}"
            ) from exc

        if not resolved_root.is_dir():
            raise WorkspaceNotFoundError(
                f"Workspace root is not a directory: {configured_root}"
            )

        self._workspace_root = resolved_root

    @property
    def workspace_root(self) -> Path:
        return self._workspace_root

    def _authorize(self, path: Path) -> tuple[Path, Path]:
        candidate = path.expanduser()
        if not candidate.is_absolute():
            candidate = self._workspace_root / candidate

        resolved = candidate.resolve(strict=False)
        is_outside = (
            resolved != self._workspace_root
            and self._workspace_root not in resolved.parents
        )
        if is_outside:
            raise WorkspacePermissionError(f"Path outside workspace root: {path}")

        return candidate, resolved

    def list_directory(self, path: Path) -> list[WorkspaceEntry]:
        candidate, _ = self._authorize(path)
        if not candidate.exists():
            raise WorkspaceNotFoundError(f"Directory not found: {path}")

        if not candidate.is_dir():
            raise WorkspaceNotFoundError(f"Not a directory: {path}")

        entries: list[WorkspaceEntry] = []

        for item in sorted(candidate.iterdir()):
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
        candidate, _ = self._authorize(path)
        if not candidate.exists():
            raise WorkspaceNotFoundError(f"File not found: {path}")

        return candidate.read_text(encoding=encoding)

    def write_file(
        self,
        path: Path,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        candidate, _ = self._authorize(path)
        candidate.write_text(content, encoding=encoding)

    def create_file(self, path: Path) -> None:
        candidate, _ = self._authorize(path)
        if candidate.exists():
            raise WorkspaceAlreadyExistsError(f"File already exists: {path}")

        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.touch()

    def create_directory(self, path: Path) -> None:
        candidate, _ = self._authorize(path)
        if candidate.exists():
            raise WorkspaceAlreadyExistsError(
                f"Directory already exists: {path}"
            )

        candidate.mkdir(parents=True)

    def move(self, source: Path, destination: Path) -> None:
        source_candidate, source_resolved = self._authorize(source)
        destination_candidate, _ = self._authorize(destination)

        if source_resolved == self._workspace_root:
            raise WorkspacePermissionError("Workspace root cannot be moved")

        if not source_candidate.exists():
            raise WorkspaceNotFoundError(f"Source not found: {source}")

        source_candidate.rename(destination_candidate)

    def delete(self, path: Path) -> None:
        candidate, resolved = self._authorize(path)

        if resolved == self._workspace_root:
            raise WorkspacePermissionError("Workspace root cannot be deleted")

        if not candidate.exists():
            raise WorkspaceNotFoundError(f"Path not found: {path}")

        if candidate.is_file():
            candidate.unlink()
        else:
            candidate.rmdir()
