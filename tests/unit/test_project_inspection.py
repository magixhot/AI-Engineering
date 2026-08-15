from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_engineering.project_inspection import (
    ProjectInspectionError,
    ProjectInspectionRequest,
    inspect_project_state,
)


def _init_repo(root: Path) -> str:
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Inspection Test",
            "-c",
            "user.email=inspection@example.invalid",
            "commit",
            "-m",
            "initial",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_inspection_returns_deterministic_portable_snapshot(tmp_path: Path) -> None:
    root = tmp_path / "project"
    (root / "docs").mkdir(parents=True)
    (root / "src" / "sample_pkg").mkdir(parents=True)
    (root / "docs" / "CURRENT_STATUS.md").write_text("status\n", encoding="utf-8")
    (root / "src" / "sample_pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nname = "sample-project"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )

    expected_head = _init_repo(root)

    first = inspect_project_state(ProjectInspectionRequest(root))
    second = inspect_project_state(ProjectInspectionRequest(root))

    assert first == second
    assert first.project_root == root.resolve()
    assert first.git_repository is True
    assert first.git_branch == "main"
    assert first.git_head == expected_head
    assert first.project_name == "sample-project"
    assert first.package_name == "sample_pkg"
    assert [entry.relative_path for entry in first.files] == sorted(
        entry.relative_path for entry in first.files
    )
    assert all("\\" not in entry.relative_path for entry in first.files)
    assert all(str(root.resolve()) not in entry.relative_path for entry in first.files)


def test_inspection_excludes_local_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "keep.txt").write_text("keep", encoding="utf-8")
    for directory in (".git", ".venv", "__pycache__", "build", "dist", ".pytest_cache"):
        path = root / directory
        path.mkdir()
        (path / "ignored.txt").write_text("ignored", encoding="utf-8")

    snapshot = inspect_project_state(ProjectInspectionRequest(root))
    paths = {entry.relative_path for entry in snapshot.files}

    assert "keep.txt" in paths
    assert not any(path.startswith(".git") for path in paths)
    assert not any(path.startswith(".venv") for path in paths)
    assert not any("__pycache__" in path for path in paths)
    assert not any(path.startswith("build") for path in paths)
    assert not any(path.startswith("dist") for path in paths)


def test_non_repository_has_no_git_claims(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()

    snapshot = inspect_project_state(ProjectInspectionRequest(root))

    assert snapshot.git_repository is False
    assert snapshot.git_branch is None
    assert snapshot.git_head is None


def test_parent_repository_does_not_make_nested_project_a_repository(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True)
    nested = tmp_path / "nested"
    nested.mkdir()

    snapshot = inspect_project_state(ProjectInspectionRequest(nested))

    assert snapshot.git_repository is False
    assert snapshot.git_branch is None
    assert snapshot.git_head is None


def test_empty_repository_reports_branch_without_head(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True)

    snapshot = inspect_project_state(ProjectInspectionRequest(root))

    assert snapshot.git_repository is True
    assert snapshot.git_branch == "main"
    assert snapshot.git_head is None


def test_multiple_src_packages_do_not_infer_package_name(tmp_path: Path) -> None:
    root = tmp_path / "project"
    for package in ("one", "two"):
        package_dir = root / "src" / package
        package_dir.mkdir(parents=True, exist_ok=True)
        (package_dir / "__init__.py").write_text("", encoding="utf-8")

    snapshot = inspect_project_state(ProjectInspectionRequest(root))

    assert snapshot.package_name is None


def test_missing_root_fails_with_controlled_error(tmp_path: Path) -> None:
    with pytest.raises(ProjectInspectionError, match="Project root"):
        inspect_project_state(ProjectInspectionRequest(tmp_path / "missing"))


def test_file_root_fails_with_controlled_error(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")

    with pytest.raises(ProjectInspectionError, match="directory"):
        inspect_project_state(ProjectInspectionRequest(target))


def test_invalid_pyproject_fails_with_controlled_error(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "pyproject.toml").write_text("[project\n", encoding="utf-8")

    with pytest.raises(ProjectInspectionError, match="pyproject.toml"):
        inspect_project_state(ProjectInspectionRequest(root))
