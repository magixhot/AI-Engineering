from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .engineering_bootstrap import PYTHON_ENGINEERING_PROFILE
from .project_templates import ProjectTemplateGenerator

PYTHON_ENGINEERING_V1_BASELINE = "python-engineering-v1"

OWNERSHIP_MACHINE = "machine_owned"
OWNERSHIP_HUMAN = "human_owned"
OWNERSHIP_MANAGED_SECTION = "managed_section"
OWNERSHIP_GENERATED_ABSENT = "generated_absent"
OWNERSHIP_UNKNOWN = "unknown"

ACTION_CREATE_FILE = "create_file"
ACTION_REPLACE_MACHINE_FILE = "replace_machine_owned_file"
ACTION_DELETE_MACHINE_FILE = "delete_machine_owned_file"

STATE_UNCHANGED_SOURCE = "unchanged_source"
STATE_ALREADY_TARGET = "already_target"
STATE_MISSING = "missing"
STATE_LOCALLY_MODIFIED = "locally_modified"
STATE_UNEXPECTED_PRESENT = "unexpected_present"
STATE_UNSUPPORTED_TYPE = "unsupported_type"
STATE_OUTSIDE_ROOT = "outside_root"
STATE_MANUAL_REVIEW = "manual_review"

_ALLOWED_OWNERSHIP = {
    OWNERSHIP_MACHINE,
    OWNERSHIP_HUMAN,
    OWNERSHIP_MANAGED_SECTION,
    OWNERSHIP_GENERATED_ABSENT,
    OWNERSHIP_UNKNOWN,
}
_ALLOWED_ACTIONS = {
    ACTION_CREATE_FILE,
    ACTION_REPLACE_MACHINE_FILE,
    ACTION_DELETE_MACHINE_FILE,
}

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
class MigrationPathRule:
    """One declared path rule within a registered migration contract."""

    path: str
    action: str
    ownership: str
    source_content: bytes | None = None
    target_content: bytes | None = None

    def __post_init__(self) -> None:
        normalized = Path(self.path)
        if not self.path or normalized.is_absolute() or ".." in normalized.parts:
            raise ValueError("migration rule path must be a bounded relative path")
        normalized_path = normalized.as_posix()
        if normalized_path in {".", ""}:
            raise ValueError("migration rule path must identify a project child")
        if self.action not in _ALLOWED_ACTIONS:
            raise ValueError(f"unsupported migration rule action: {self.action!r}")
        if self.ownership not in _ALLOWED_OWNERSHIP:
            raise ValueError(f"unsupported migration ownership: {self.ownership!r}")
        if self.action == ACTION_CREATE_FILE:
            if self.source_content is not None or self.target_content is None:
                raise ValueError(
                    "create_file requires target_content and no source_content"
                )
        elif self.action == ACTION_REPLACE_MACHINE_FILE:
            if self.source_content is None or self.target_content is None:
                raise ValueError(
                    "replace_machine_owned_file requires source and target content"
                )
        elif self.action == ACTION_DELETE_MACHINE_FILE:
            if self.source_content is None or self.target_content is not None:
                raise ValueError(
                    "delete_machine_owned_file requires source content only"
                )
        object.__setattr__(self, "path", normalized_path)


@dataclass(frozen=True)
class MigrationContract:
    """One explicit registered source-to-target migration edge."""

    migration_id: str
    source_baselines: tuple[str, ...]
    target_baseline: str
    profiles: tuple[str, ...]
    rules: tuple[MigrationPathRule, ...] = ()

    def __post_init__(self) -> None:
        migration_id = self.migration_id.strip()
        target_baseline = self.target_baseline.strip()
        source_baselines = tuple(sorted(set(self.source_baselines)))
        profiles = tuple(sorted(set(self.profiles)))
        rules = tuple(sorted(self.rules, key=lambda item: (item.path, item.action)))
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
        paths = [rule.path.casefold() for rule in rules]
        if len(paths) != len(set(paths)):
            raise ValueError("migration rule paths must be unique")
        object.__setattr__(self, "migration_id", migration_id)
        object.__setattr__(self, "target_baseline", target_baseline)
        object.__setattr__(self, "source_baselines", source_baselines)
        object.__setattr__(self, "profiles", profiles)
        object.__setattr__(self, "rules", rules)


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


@dataclass(frozen=True)
class ProjectMigrationRequest:
    """Read-only request for one exact registered migration edge."""

    project_root: Path
    migration_id: str


@dataclass(frozen=True)
class ProjectMigrationObservation:
    """Observed state for one migration-declared project path."""

    path: str
    ownership: str
    state: str
    original_sha256: str | None


@dataclass(frozen=True)
class ProjectMigrationOperation:
    """One safe operation produced by read-only migration planning."""

    path: str
    action: str
    ownership: str
    original_sha256: str | None
    replacement_content: bytes | None


@dataclass(frozen=True)
class ProjectMigrationPlan:
    """Deterministic AUTO-0004 dry-run plan with explicit blockers."""

    project_root: Path
    migration_id: str
    source_baseline: str
    target_baseline: str
    observations: tuple[ProjectMigrationObservation, ...]
    operations: tuple[ProjectMigrationOperation, ...]
    manual_review: tuple[str, ...]

    @property
    def is_applicable(self) -> bool:
        return not self.manual_review


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


def _observation(
    rule: MigrationPathRule,
    state: str,
    content: bytes | None = None,
) -> ProjectMigrationObservation:
    return ProjectMigrationObservation(
        path=rule.path,
        ownership=rule.ownership,
        state=state,
        original_sha256=_digest(content) if content is not None else None,
    )


def _blocked(
    rule: MigrationPathRule,
    state: str,
    content: bytes | None = None,
) -> tuple[ProjectMigrationObservation, None, str]:
    return (
        _observation(rule, state, content),
        None,
        f"{rule.path}: {state}",
    )


def _inspect_rule(
    root: Path,
    rule: MigrationPathRule,
) -> tuple[
    ProjectMigrationObservation,
    ProjectMigrationOperation | None,
    str | None,
]:
    path = root / rule.path
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return _blocked(rule, STATE_UNSUPPORTED_TYPE)
    if not resolved.is_relative_to(root):
        return _blocked(rule, STATE_OUTSIDE_ROOT)
    if path.is_symlink():
        return _blocked(rule, STATE_UNSUPPORTED_TYPE)

    if rule.ownership in {
        OWNERSHIP_HUMAN,
        OWNERSHIP_MANAGED_SECTION,
        OWNERSHIP_UNKNOWN,
    }:
        content = path.read_bytes() if path.is_file() else None
        return _blocked(rule, STATE_MANUAL_REVIEW, content)

    if rule.action == ACTION_CREATE_FILE:
        if not path.exists():
            observation = _observation(rule, STATE_MISSING)
            operation = ProjectMigrationOperation(
                path=rule.path,
                action=rule.action,
                ownership=rule.ownership,
                original_sha256=None,
                replacement_content=rule.target_content,
            )
            return observation, operation, None
        if not path.is_file():
            return _blocked(rule, STATE_UNSUPPORTED_TYPE)
        content = path.read_bytes()
        if content == rule.target_content:
            return _observation(rule, STATE_ALREADY_TARGET, content), None, None
        return _blocked(rule, STATE_UNEXPECTED_PRESENT, content)

    if not path.exists():
        if rule.action == ACTION_DELETE_MACHINE_FILE:
            return _observation(rule, STATE_ALREADY_TARGET), None, None
        return _blocked(rule, STATE_MISSING)
    if not path.is_file():
        return _blocked(rule, STATE_UNSUPPORTED_TYPE)

    content = path.read_bytes()
    if rule.action == ACTION_REPLACE_MACHINE_FILE:
        if content == rule.target_content:
            return _observation(rule, STATE_ALREADY_TARGET, content), None, None
        if content != rule.source_content:
            return _blocked(rule, STATE_LOCALLY_MODIFIED, content)
        if rule.ownership != OWNERSHIP_MACHINE:
            return _blocked(rule, STATE_MANUAL_REVIEW, content)
        digest = _digest(content)
        observation = _observation(rule, STATE_UNCHANGED_SOURCE, content)
        operation = ProjectMigrationOperation(
            path=rule.path,
            action=rule.action,
            ownership=rule.ownership,
            original_sha256=digest,
            replacement_content=rule.target_content,
        )
        return observation, operation, None

    if content != rule.source_content:
        return _blocked(rule, STATE_LOCALLY_MODIFIED, content)
    if rule.ownership != OWNERSHIP_MACHINE:
        return _blocked(rule, STATE_MANUAL_REVIEW, content)
    digest = _digest(content)
    observation = _observation(rule, STATE_UNCHANGED_SOURCE, content)
    operation = ProjectMigrationOperation(
        path=rule.path,
        action=rule.action,
        ownership=rule.ownership,
        original_sha256=digest,
        replacement_content=None,
    )
    return observation, operation, None


def plan_project_migration(
    request: ProjectMigrationRequest,
    registry: MigrationRegistry = DEFAULT_MIGRATION_REGISTRY,
) -> ProjectMigrationPlan:
    """Produce a deterministic read-only plan for one registered migration."""

    identity = detect_project_identity(request.project_root)
    contract = registry.resolve(request.migration_id, identity)
    observations: list[ProjectMigrationObservation] = []
    operations: list[ProjectMigrationOperation] = []
    manual_review: list[str] = []

    for rule in contract.rules:
        observation, operation, blocker = _inspect_rule(
            identity.project_root,
            rule,
        )
        observations.append(observation)
        if operation is not None:
            operations.append(operation)
        if blocker is not None:
            manual_review.append(blocker)

    return ProjectMigrationPlan(
        project_root=identity.project_root,
        migration_id=contract.migration_id,
        source_baseline=identity.baseline,
        target_baseline=contract.target_baseline,
        observations=tuple(observations),
        operations=tuple(operations),
        manual_review=tuple(manual_review),
    )
