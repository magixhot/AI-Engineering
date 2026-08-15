from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .project_templates import (
    ProjectTemplateError,
    ProjectTemplateGenerator,
    StandaloneProject,
    StandaloneProjectRequest,
    create_standalone_project,
)

PYTHON_ENGINEERING_PROFILE = "python-engineering"


class EngineeringBootstrapError(Exception):
    """Controlled AUTO-0001 bootstrap failure."""


@dataclass(frozen=True)
class EngineeringBootstrapRequest:
    """Typed input for a bounded engineering-project bootstrap."""

    target_directory: Path
    project_name: str
    project_description: str
    author: str | None = None
    profile: str = PYTHON_ENGINEERING_PROFILE


@dataclass(frozen=True)
class EngineeringBootstrapVerification:
    """Read-only evidence for the invariants claimed by AUTO-0001 V1."""

    required_files_present: bool
    git_repository: bool
    default_branch: str
    initial_commit_present: bool
    python_package_present: bool
    smoke_test_present: bool


@dataclass(frozen=True)
class EngineeringBootstrapResult:
    """Result of creating and verifying one engineering bootstrap project."""

    project: StandaloneProject
    profile: str
    package_name: str
    verification: EngineeringBootstrapVerification


def _run_git(target: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=target,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise EngineeringBootstrapError(
            f"Bootstrap verification failed while running git {' '.join(args)}"
        ) from exc
    return result.stdout.rstrip("\r\n")


def _expected_relative_files(package_name: str) -> set[str]:
    return {
        *ProjectTemplateGenerator.REQUIRED_DOCS,
        "pyproject.toml",
        ".gitignore",
        f"src/{package_name}/__init__.py",
        "tests/test_smoke.py",
    }


def _verify_bootstrap(
    project: StandaloneProject,
    package_name: str,
) -> EngineeringBootstrapVerification:
    target = project.target_directory.resolve()
    expected_relative_files = _expected_relative_files(package_name)

    generated_relative_files: set[str] = set()
    for generated_path in project.generated_files:
        resolved_path = generated_path.resolve()
        if not resolved_path.is_relative_to(target):
            raise EngineeringBootstrapError(
                f"Bootstrap verification failed: generated path escapes target: "
                f"{generated_path}"
            )
        generated_relative_files.add(resolved_path.relative_to(target).as_posix())

    if generated_relative_files != expected_relative_files:
        raise EngineeringBootstrapError(
            "Bootstrap verification failed: generated file set does not match "
            "the python-engineering profile"
        )

    missing_files = sorted(
        relative_path
        for relative_path in expected_relative_files
        if not (target / relative_path).is_file()
    )
    if missing_files:
        raise EngineeringBootstrapError(
            "Bootstrap verification failed: missing required files: "
            + ", ".join(missing_files)
        )

    git_root = Path(_run_git(target, "rev-parse", "--show-toplevel")).resolve()
    if git_root != target:
        raise EngineeringBootstrapError(
            f"Bootstrap verification failed: Git root is {git_root}, expected {target}"
        )

    default_branch = _run_git(target, "branch", "--show-current")
    if default_branch != "main":
        raise EngineeringBootstrapError(
            "Bootstrap verification failed: default branch is "
            f"{default_branch!r}, expected 'main'"
        )

    _run_git(target, "rev-parse", "--verify", "HEAD")
    committed_output = _run_git(target, "ls-tree", "--name-only", "-r", "HEAD")
    committed_files = {line for line in committed_output.splitlines() if line}
    if not expected_relative_files.issubset(committed_files):
        missing_committed = sorted(expected_relative_files - committed_files)
        raise EngineeringBootstrapError(
            "Bootstrap verification failed: generated files missing from initial "
            "commit: " + ", ".join(missing_committed)
        )

    package_file = target / "src" / package_name / "__init__.py"
    smoke_test = target / "tests" / "test_smoke.py"
    return EngineeringBootstrapVerification(
        required_files_present=True,
        git_repository=True,
        default_branch=default_branch,
        initial_commit_present=True,
        python_package_present=package_file.is_file(),
        smoke_test_present=smoke_test.is_file(),
    )


def bootstrap_engineering_project(
    request: EngineeringBootstrapRequest,
) -> EngineeringBootstrapResult:
    """Create and verify one AUTO-0001 V1 engineering project."""

    if request.profile != PYTHON_ENGINEERING_PROFILE:
        raise EngineeringBootstrapError(
            f"Unsupported engineering bootstrap profile: {request.profile!r}"
        )

    try:
        package_name = ProjectTemplateGenerator._derive_package_name(
            request.project_name
        )
        project = create_standalone_project(
            StandaloneProjectRequest(
                target_directory=request.target_directory,
                project_name=request.project_name,
                project_description=request.project_description,
                author=request.author,
                include_python_scaffold=True,
            )
        )
    except ProjectTemplateError as exc:
        raise EngineeringBootstrapError(str(exc)) from exc

    verification = _verify_bootstrap(project, package_name)
    return EngineeringBootstrapResult(
        project=project,
        profile=request.profile,
        package_name=package_name,
        verification=verification,
    )
