from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering.mcp import create_server
from ai_engineering.workspace.exceptions import (
    WorkspaceAlreadyExistsError,
    WorkspaceNotFoundError,
)
from ai_engineering.workspace.service import WorkspaceService


def test_workspace_tools_are_registered() -> None:
    server = create_server()

    assert server.registry.exists("workspace.list")
    assert server.registry.exists("workspace.read_file")


def test_list_directory_returns_sorted_entry_metadata(tmp_path: Path) -> None:
    service = WorkspaceService()
    (tmp_path / "b.txt").write_text("two", encoding="utf-8")
    (tmp_path / "a-directory").mkdir()

    entries = service.list_directory(tmp_path)

    metadata = [
        (entry.path.name, entry.is_file, entry.is_directory, entry.size)
        for entry in entries
    ]

    assert metadata == [
        ("a-directory", False, True, 0),
        ("b.txt", True, False, 3),
    ]


def test_list_directory_rejects_missing_and_file_paths(tmp_path: Path) -> None:
    service = WorkspaceService()
    file_path = tmp_path / "file.txt"
    file_path.write_text("content", encoding="utf-8")

    with pytest.raises(WorkspaceNotFoundError, match="Directory not found"):
        service.list_directory(tmp_path / "missing")

    with pytest.raises(WorkspaceNotFoundError, match="Not a directory"):
        service.list_directory(file_path)


def test_read_file_returns_utf8_content_and_rejects_missing_path(
    tmp_path: Path,
) -> None:
    service = WorkspaceService()
    file_path = tmp_path / "message.txt"
    file_path.write_text("Tere, maailm", encoding="utf-8")

    assert service.read_file(file_path) == "Tere, maailm"

    with pytest.raises(WorkspaceNotFoundError, match="File not found"):
        service.read_file(tmp_path / "missing.txt")


def test_read_file_on_directory_preserves_current_os_error(tmp_path: Path) -> None:
    service = WorkspaceService()

    with pytest.raises(OSError):
        service.read_file(tmp_path)


def test_write_file_creates_and_overwrites_a_fixture_file(tmp_path: Path) -> None:
    service = WorkspaceService()
    file_path = tmp_path / "written.txt"

    service.write_file(file_path, "first")
    service.write_file(file_path, "second")

    assert file_path.read_text(encoding="utf-8") == "second"


def test_write_file_invalid_target_preserves_current_os_error(tmp_path: Path) -> None:
    service = WorkspaceService()
    target = tmp_path / "missing-parent" / "written.txt"

    with pytest.raises(FileNotFoundError):
        service.write_file(target, "content")

    assert not target.parent.exists()


def test_create_file_creates_missing_parents_and_rejects_existing_file(
    tmp_path: Path,
) -> None:
    service = WorkspaceService()
    file_path = tmp_path / "nested" / "new.txt"

    service.create_file(file_path)

    assert file_path.is_file()
    with pytest.raises(WorkspaceAlreadyExistsError, match="File already exists"):
        service.create_file(file_path)


def test_create_directory_creates_missing_parents_and_rejects_existing_path(
    tmp_path: Path,
) -> None:
    service = WorkspaceService()
    directory = tmp_path / "nested" / "directory"

    service.create_directory(directory)

    assert directory.is_dir()
    with pytest.raises(WorkspaceAlreadyExistsError, match="Directory already exists"):
        service.create_directory(directory)


def test_move_moves_a_fixture_file_and_rejects_missing_or_conflicting_source(
    tmp_path: Path,
) -> None:
    service = WorkspaceService()
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"
    source.write_text("content", encoding="utf-8")

    service.move(source, destination)

    assert not source.exists()
    assert destination.read_text(encoding="utf-8") == "content"
    with pytest.raises(WorkspaceNotFoundError, match="Source not found"):
        service.move(source, tmp_path / "other.txt")

    replacement = tmp_path / "replacement.txt"
    replacement.write_text("replacement", encoding="utf-8")
    with pytest.raises(FileExistsError):
        service.move(replacement, destination)


def test_delete_removes_file_and_empty_directory_and_preserves_os_errors(
    tmp_path: Path,
) -> None:
    service = WorkspaceService()
    file_path = tmp_path / "delete.txt"
    directory = tmp_path / "empty"
    non_empty_directory = tmp_path / "non-empty"
    file_path.write_text("content", encoding="utf-8")
    directory.mkdir()
    non_empty_directory.mkdir()
    (non_empty_directory / "child.txt").write_text("content", encoding="utf-8")

    service.delete(file_path)
    service.delete(directory)

    assert not file_path.exists()
    assert not directory.exists()
    with pytest.raises(WorkspaceNotFoundError, match="Path not found"):
        service.delete(tmp_path / "missing")
    with pytest.raises(OSError):
        service.delete(non_empty_directory)

    assert (non_empty_directory / "child.txt").is_file()
