"""Read-only project-state inspection for AUTO-0002."""

from __future__ import annotations

import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path

_EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "venv",
}


class ProjectInspectionError(RuntimeError):
    """Raised when a project root cannot be inspected safely."""


@dataclass(frozen=True)
class ProjectInspectionRequest:
    project_root: Path


@dataclass(frozen=True)
class ProjectFileEntry:
    relative_path: str
    kind: str


@dataclass(frozen=True)
class ProjectStateSnapshot:
    project_root: Path
    files: tuple[ProjectFileEntry, ...]
    git_repository: bool
    git_branch: str | None
    git_head: str | None
    package_name: str | None
    project_name: str | None


def _portable_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_excluded(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return any(part in _EXCLUDED_PARTS for part in relative.parts)


def _inspect_files(root: Path) -> tuple[ProjectFileEntry, ...]:
    entries: list[ProjectFileEntry] = []
    for path in root.rglob("*"):
        if _is_excluded(path, root):
            continue
        if path.is_dir():
            kind = "directory"
        elif path.is_file():
            kind = "file"
        else:
            continue
        entries.append(ProjectFileEntry(_portable_relative(path, root), kind))
    return tuple(sorted(entries, key=lambda entry: (entry.relative_path, entry.kind)))


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _inspect_git(root: Path) -> tuple[bool, str | None, str | None]:
    top_level = _run_git(root, "rev-parse", "--show-toplevel")
    if top_level.returncode != 0:
        return False, None, None

    try:
        discovered_root = Path(top_level.stdout.strip()).resolve()
    except OSError as error:
        raise ProjectInspectionError("Git repository root could not be resolved") from error

    if discovered_root != root:
        return False, None, None

    branch_result = _run_git(root, "branch", "--show-current")
    if branch_result.returncode != 0:
        raise ProjectInspectionError("Git branch inspection failed")
    branch = branch_result.stdout.strip() or None

    head_result = _run_git(root, "rev-parse", "HEAD")
    if head_result.returncode == 0:
        head = head_result.stdout.strip() or None
    else:
        head = None

    return True, branch, head


def _inspect_pyproject(root: Path) -> tuple[str | None, str | None]:
    pyproject = root / "pyproject.toml"
    project_name: str | None = None
    if pyproject.is_file():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as error:
            raise ProjectInspectionError("pyproject.toml could not be inspected") from error
        project = data.get("project")
        if isinstance(project, dict):
            value = project.get("name")
            if isinstance(value, str) and value.strip():
                project_name = value.strip()

    package_name: str | None = None
    src = root / "src"
    if src.is_dir():
        packages = sorted(
            child.name
            for child in src.iterdir()
            if child.is_dir() and (child / "__init__.py").is_file()
        )
        if len(packages) == 1:
            package_name = packages[0]

    return package_name, project_name


def inspect_project_state(request: ProjectInspectionRequest) -> ProjectStateSnapshot:
    """Return a deterministic, read-only snapshot of approved local project state."""

    try:
        root = request.project_root.resolve(strict=True)
    except (FileNotFoundError, OSError) as error:
        raise ProjectInspectionError("Project root does not exist or cannot be resolved") from error

    if not root.is_dir():
        raise ProjectInspectionError("Project root must be a directory")

    try:
        files = _inspect_files(root)
        git_repository, git_branch, git_head = _inspect_git(root)
        package_name, project_name = _inspect_pyproject(root)
    except PermissionError as error:
        raise ProjectInspectionError("Project root is not readable") from error

    return ProjectStateSnapshot(
        project_root=root,
        files=files,
        git_repository=git_repository,
        git_branch=git_branch,
        git_head=git_head,
        package_name=package_name,
        project_name=project_name,
    )
