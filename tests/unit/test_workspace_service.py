from __future__ import annotations

import os
from pathlib import Path

import pytest

from ai_engineering.mcp import create_server
from ai_engineering.workspace.exceptions import (
    WorkspaceAlreadyExistsError,
    WorkspaceNotFoundError,
    WorkspacePermissionError,
)
from ai_engineering.workspace.service import WorkspaceService


def service_for(tmp_path: Path) -> WorkspaceService:
    return WorkspaceService(tmp_path)


def test_workspace_tools_are_registered() -> None:
    server = create_server()
    assert server.registry.exists("workspace.list")
    assert server.registry.exists("workspace.read_file")


def test_service_captures_resolved_workspace_root(tmp_path: Path) -> None:
    service = WorkspaceService(tmp_path / ".")
    assert service.workspace_root == tmp_path.resolve()


def test_service_rejects_missing_or_file_workspace_root(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceNotFoundError, match="Workspace root not found"):
        WorkspaceService(tmp_path / "missing")

    file_root = tmp_path / "file.txt"
    file_root.write_text("x", encoding="utf-8")
    with pytest.raises(WorkspaceNotFoundError, match="not a directory"):
        WorkspaceService(file_root)


def test_list_directory_returns_sorted_entry_metadata(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    (tmp_path / "b.txt").write_text("two", encoding="utf-8")
    (tmp_path / "a-directory").mkdir()

    entries = service.list_directory(Path("."))
    metadata = [
        (entry.path.name, entry.is_file, entry.is_directory, entry.size)
        for entry in entries
    ]
    assert metadata == [
        ("a-directory", False, True, 0),
        ("b.txt", True, False, 3),
    ]


def test_relative_and_absolute_in_root_paths_are_allowed(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    file_path = tmp_path / "message.txt"
    file_path.write_text("content", encoding="utf-8")

    assert service.read_file(Path("message.txt")) == "content"
    assert service.read_file(file_path) == "content"


def test_outside_paths_are_rejected_before_existence_checks(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    service = service_for(root)
    outside = tmp_path / "outside.txt"

    with pytest.raises(WorkspacePermissionError, match="outside workspace root"):
        service.read_file(Path("../outside.txt"))
    with pytest.raises(WorkspacePermissionError, match="outside workspace root"):
        service.read_file(outside)


def test_sibling_prefix_is_not_treated_as_contained(tmp_path: Path) -> None:
    root = tmp_path / "work"
    sibling = tmp_path / "work-other"
    root.mkdir()
    sibling.mkdir()
    service = service_for(root)

    with pytest.raises(WorkspacePermissionError):
        service.list_directory(sibling)


def test_prospective_write_and_create_paths_cannot_escape(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    service = service_for(root)

    with pytest.raises(WorkspacePermissionError):
        service.write_file(Path("../written.txt"), "content")
    with pytest.raises(WorkspacePermissionError):
        service.create_file(Path("../nested/new.txt"))
    with pytest.raises(WorkspacePermissionError):
        service.create_directory(Path("../nested/directory"))

    assert not (tmp_path / "written.txt").exists()
    assert not (tmp_path / "nested").exists()


def test_symlink_escape_is_rejected_when_supported(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "secret.txt").write_text("secret", encoding="utf-8")
    link = root / "escape"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink fixture unavailable: {exc}")

    service = service_for(root)
    with pytest.raises(WorkspacePermissionError):
        service.read_file(Path("escape/secret.txt"))


def test_list_directory_rejects_missing_and_file_paths(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    file_path = tmp_path / "file.txt"
    file_path.write_text("content", encoding="utf-8")

    with pytest.raises(WorkspaceNotFoundError, match="Directory not found"):
        service.list_directory(Path("missing"))
    with pytest.raises(WorkspaceNotFoundError, match="Not a directory"):
        service.list_directory(Path("file.txt"))


def test_read_file_returns_utf8_content_and_rejects_missing_path(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    file_path = tmp_path / "message.txt"
    file_path.write_text("Tere, maailm", encoding="utf-8")

    assert service.read_file(Path("message.txt")) == "Tere, maailm"
    with pytest.raises(WorkspaceNotFoundError, match="File not found"):
        service.read_file(Path("missing.txt"))


def test_read_file_on_directory_preserves_current_os_error(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    with pytest.raises(OSError):
        service.read_file(Path("."))


def test_write_file_creates_and_overwrites_a_fixture_file(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    service.write_file(Path("written.txt"), "first")
    service.write_file(Path("written.txt"), "second")
    assert (tmp_path / "written.txt").read_text(encoding="utf-8") == "second"


def test_write_file_invalid_target_preserves_current_os_error(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    target = Path("missing-parent/written.txt")
    with pytest.raises(FileNotFoundError):
        service.write_file(target, "content")
    assert not (tmp_path / "missing-parent").exists()


def test_create_file_creates_missing_parents_and_rejects_existing_file(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    file_path = Path("nested/new.txt")
    service.create_file(file_path)
    assert (tmp_path / file_path).is_file()
    with pytest.raises(WorkspaceAlreadyExistsError, match="File already exists"):
        service.create_file(file_path)


def test_create_directory_creates_missing_parents_and_rejects_existing_path(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    directory = Path("nested/directory")
    service.create_directory(directory)
    assert (tmp_path / directory).is_dir()
    with pytest.raises(WorkspaceAlreadyExistsError, match="Directory already exists"):
        service.create_directory(directory)


def test_move_authorizes_both_endpoints_and_protects_root(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    service = service_for(root)
    source = root / "source.txt"
    source.write_text("content", encoding="utf-8")

    with pytest.raises(WorkspacePermissionError):
        service.move(tmp_path / "outside.txt", Path("destination.txt"))
    with pytest.raises(WorkspacePermissionError):
        service.move(Path("source.txt"), tmp_path / "outside.txt")
    with pytest.raises(WorkspacePermissionError, match="root cannot be moved"):
        service.move(Path("."), Path("nested-root"))

    assert source.exists()


def test_move_preserves_current_platform_conflict_behavior(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"
    source.write_text("content", encoding="utf-8")

    service.move(Path("source.txt"), Path("destination.txt"))
    assert not source.exists()
    assert destination.read_text(encoding="utf-8") == "content"

    replacement = tmp_path / "replacement.txt"
    replacement.write_text("replacement", encoding="utf-8")
    if os.name == "nt":
        with pytest.raises(FileExistsError):
            service.move(Path("replacement.txt"), Path("destination.txt"))
        assert replacement.read_text(encoding="utf-8") == "replacement"
        assert destination.read_text(encoding="utf-8") == "content"
    else:
        service.move(Path("replacement.txt"), Path("destination.txt"))
        assert not replacement.exists()
        assert destination.read_text(encoding="utf-8") == "replacement"


def test_delete_protects_root_and_preserves_existing_errors(tmp_path: Path) -> None:
    service = service_for(tmp_path)
    file_path = tmp_path / "delete.txt"
    directory = tmp_path / "empty"
    non_empty_directory = tmp_path / "non-empty"
    file_path.write_text("content", encoding="utf-8")
    directory.mkdir()
    non_empty_directory.mkdir()
    (non_empty_directory / "child.txt").write_text("content", encoding="utf-8")

    service.delete(Path("delete.txt"))
    service.delete(Path("empty"))
    assert not file_path.exists()
    assert not directory.exists()

    with pytest.raises(WorkspacePermissionError, match="root cannot be deleted"):
        service.delete(Path("."))
    with pytest.raises(WorkspaceNotFoundError, match="Path not found"):
        service.delete(Path("missing"))
    with pytest.raises(OSError):
        service.delete(Path("non-empty"))
    assert (non_empty_directory / "child.txt").is_file()
