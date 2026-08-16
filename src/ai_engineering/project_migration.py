from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .engineering_bootstrap import PYTHON_ENGINEERING_PROFILE
from .project_templates import ProjectTemplateGenerator

PYTHON_ENGINEERING_V1_BASELINE = "python-engineering-v1"

_EXPECTED_GITIGNORE = (
    "__pycache__/\n"
    "*.py[cod]\n"
    ".venv/\n"
    "venv/\n"
    ".coverage\n"
    "htmlcov/\n"
    "build/\n"
    "dist/\n"
    "*.egg-info/\n"
    ".idea/\n"
    ".vscode/\n"
).encode()


class ProjectMigrationError(Exception):
    """Controlled AUTO-0004 project migration failure."""


class UnsupportedProjectIdentityError(ProjectMigrationError):
    """The project cannot be positively identified as a supported baseline."""


class UnsupportedMigrationError(ProjectMigrationError):
    """The requested migration is not registered for the detected identity."""


@dataclass(frozen=True)
class ProjectIdentity:
    """Read-only positive identity for one supported engineering project."""

    project_root: Path
    profile: str
    baseline: str
    distribution_name: str
    package_name: str
    project_version: str
    evidence_sha256: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class MigrationContract:
    """One explicit registered source-to-target migration edge."""

    migration_id: str
    source_baselines: tuple[str, ...]
    target_baseline: str
    profiles: tuple[str, ...]

    def __post_init__(self) -> None:
        migration_id = self.migration_id.strip()
        target_baseline = self.target_baseline.strip()
        source_baselines = tuple(sorted(set(self.source_baselines)))
        profiles = tuple(sorted(set(self.profiles)))
        if not migration_id:
            raise ValueError("migration_id must not be empty")
        if not target_baseline:
            raise ValueError("target_baseline must not be empty")
        if not source_baselines:
            raise ValueError("source_baselines must not be empty")
        if not profiles:
            raise ValueError("profiles must not be empty")
        if any(not value.strip() for value in source_baselines):
            raise ValueError("source_baselines must not contain empty values")
        if any(not value.strip() for value in profiles):
            raise ValueError("profiles must not contain empty values")
        object.__setattr__(self, "migration_id", migration_id)
        object.__setattr__(self, "target_baseline", target_baseline)
        object.__setattr__(self, "source_baselines", source_baselines)
        object.__setattr__(self, "profiles", profiles)


class MigrationRegistry:
    """Deterministic immutable registry for exact migration contracts."""

    def __init__(self, contracts: Iterable[MigrationContract] = ()) -> None:
        ordered = tuple(sorted(contracts, key=lambda item: item.migration_id))
        ids = [item.migration_id for item in ordered]
        if len(ids) != len(set(ids)):
            raise ValueError("migration ids must be unique")
        self._contracts = ordered

    @property
    def contracts(self) -> tuple[MigrationContract, ...]:
        return self._contracts

    def resolve(
        self,
        migration_id: str,
        identity: ProjectIdentity,
    ) -> MigrationContract:
        match = next(
            (item for item in self._contracts if item.migration_id == migration_id),
            None,
        )
        if match is None:
            raise UnsupportedMigrationError(
                f"Unsupported migration id: {migration_id!r}"
            )
        if identity.profile not in match.profiles:
            raise UnsupportedMigrationError(
                f"Migration {migration_id!r} does not support profile "
                f"{identity.profile!r}"
            )
        if identity.baseline not in match.source_baselines:
            raise UnsupportedMigrationError(
                f"Migration {migration_id!r} does not support source baseline "
                f"{identity.baseline!r}"
            )
        return match


DEFAULT_MIGRATION_REGISTRY = MigrationRegistry()


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _read_supported_file(root: Path, relative_path: str) -> bytes:
    path = root / relative_path
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise UnsupportedProjectIdentityError(
            f"Required identity path is unavailable: {relative_path}"
        ) from exc
    if not resolved.is_relative_to(root):
        raise UnsupportedProjectIdentityError(
            f"Required identity path escapes project root: {relative_path}"
        )
    if path.is_symlink() or not path.is_file():
        raise UnsupportedProjectIdentityError(
            f"Required identity path is not a regular file: {relative_path}"
        )
    try:
        return path.read_bytes()
    except OSError as exc:
        raise UnsupportedProjectIdentityError(
            f"Required identity path is unreadable: {relative_path}"
        ) from exc


def _expect(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise UnsupportedProjectIdentityError(
            f"Unsupported python-engineering baseline field: {field}"
        )


def _parse_pyproject(content: bytes) -> dict[str, Any]:
    try:
        parsed = tomllib.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise UnsupportedProjectIdentityError(
            "pyproject.toml is not valid UTF-8 TOML"
        ) from exc
    if not isinstance(parsed, dict):
        raise UnsupportedProjectIdentityError("pyproject.toml has unsupported shape")
    return parsed


def _validate_python_engineering_v1(
    root: Path,
    pyproject_content: bytes,
) -> ProjectIdentity:
    data = _parse_pyproject(pyproject_content)
    build_system = data.get("build-system")
    project = data.get("project")
    tool = data.get("tool")
    if not isinstance(build_system, dict) or not isinstance(project, dict):
        raise UnsupportedProjectIdentityError(
            "pyproject.toml does not identify a python-engineering project"
        )
    if not isinstance(tool, dict):
        raise UnsupportedProjectIdentityError(
            "pyproject.toml is missing required tool configuration"
        )

    _expect(build_system.get("requires"), ["setuptools>=68"], "build-system.requires")
    _expect(
        build_system.get("build-backend"),
        "setuptools.build_meta",
        "build-system.build-backend",
    )
    _expect(project.get("version"), "0.1.0", "project.version")
    _expect(project.get("requires-python"), ">=3.11", "project.requires-python")
    _expect(project.get("dependencies"), [], "project.dependencies")

    optional = project.get("optional-dependencies")
    if not isinstance(optional, dict):
        raise UnsupportedProjectIdentityError(
            "pyproject.toml is missing optional-dependencies"
        )
    _expect(
        optional.get("dev"),
        ["pytest>=8", "ruff>=0.6", "mypy>=1.11"],
        "project.optional-dependencies.dev",
    )

    pytest_config = tool.get("pytest", {}).get("ini_options")
    ruff_config = tool.get("ruff")
    mypy_config = tool.get("mypy")
    if not isinstance(pytest_config, dict):
        raise UnsupportedProjectIdentityError("pytest configuration is unsupported")
    if not isinstance(ruff_config, dict) or not isinstance(mypy_config, dict):
        raise UnsupportedProjectIdentityError("tool configuration is unsupported")
    _expect(
        pytest_config.get("testpaths"),
        ["tests"],
        "tool.pytest.ini_options.testpaths",
    )
    _expect(ruff_config.get("line-length"), 88, "tool.ruff.line-length")
    _expect(ruff_config.get("target-version"), "py311", "tool.ruff.target-version")
    lint = ruff_config.get("lint")
    if not isinstance(lint, dict):
        raise UnsupportedProjectIdentityError("ruff lint configuration is unsupported")
    _expect(lint.get("select"), ["E", "F", "I"], "tool.ruff.lint.select")
    _expect(mypy_config.get("python_version"), "3.11", "tool.mypy.python_version")
    _expect(mypy_config.get("files"), ["src", "tests"], "tool.mypy.files")
    _expect(
        mypy_config.get("warn_unused_configs"),
        True,
        "tool.mypy.warn_unused_configs",
    )

    distribution_name = project.get("name")
    if not isinstance(distribution_name, str) or not distribution_name.strip():
        raise UnsupportedProjectIdentityError("project.name is missing or invalid")
    package_name = distribution_name.replace("-", "_")
    if not package_name.isascii() or not package_name.isidentifier():
        raise UnsupportedProjectIdentityError(
            "project.name does not map to the approved package naming contract"
        )

    evidence: list[tuple[str, str]] = [("pyproject.toml", _digest(pyproject_content))]
    expected_files = {
        ".gitignore": _EXPECTED_GITIGNORE,
        f"src/{package_name}/__init__.py": (
            f'"""{package_name} package."""\n'.encode()
        ),
        "tests/test_smoke.py": (
            '"""Smoke test for the generated package."""\n\n'
            "from importlib import import_module\n\n\n"
            "def test_package_is_importable() -> None:\n"
            f'    module = import_module("{package_name}")\n'
            "    assert module is not None\n"
        ).encode(),
    }
    for relative_path, expected_content in expected_files.items():
        content = _read_supported_file(root, relative_path)
        if content != expected_content:
            raise UnsupportedProjectIdentityError(
                f"Required baseline file differs from python-engineering V1: "
                f"{relative_path}"
            )
        evidence.append((relative_path, _digest(content)))

    for relative_path in ProjectTemplateGenerator.REQUIRED_DOCS:
        content = _read_supported_file(root, relative_path)
        evidence.append((relative_path, _digest(content)))

    return ProjectIdentity(
        project_root=root,
        profile=PYTHON_ENGINEERING_PROFILE,
        baseline=PYTHON_ENGINEERING_V1_BASELINE,
        distribution_name=distribution_name,
        package_name=package_name,
        project_version="0.1.0",
        evidence_sha256=tuple(sorted(evidence)),
    )


def detect_project_identity(project_root: Path) -> ProjectIdentity:
    """Positively identify one supported project baseline without mutation."""

    try:
        root = project_root.resolve(strict=True)
    except OSError as exc:
        raise UnsupportedProjectIdentityError(
            f"Project root is unavailable: {project_root}"
        ) from exc
    if not root.is_dir():
        raise UnsupportedProjectIdentityError(
            f"Project root is not a directory: {project_root}"
        )
    pyproject_content = _read_supported_file(root, "pyproject.toml")
    return _validate_python_engineering_v1(root, pyproject_content)
