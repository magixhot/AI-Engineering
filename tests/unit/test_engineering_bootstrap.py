from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import ai_engineering.engineering_bootstrap as bootstrap_module
from ai_engineering.engineering_bootstrap import (
    PYTHON_ENGINEERING_PROFILE,
    EngineeringBootstrapError,
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_templates import create_standalone_project


def _committed_files(target: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-tree", "--name-only", "-r", "HEAD"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    )
    return {line for line in result.stdout.splitlines() if line}


def test_bootstrap_creates_and_verifies_python_engineering_project(
    tmp_path: Path,
) -> None:
    target = tmp_path / "engineering-project"

    result = bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=target,
            project_name="Engineering Project",
            project_description="A bootstrapped engineering project.",
            author="Bootstrap Author",
        )
    )

    assert result.profile == PYTHON_ENGINEERING_PROFILE
    assert result.package_name == "engineering_project"
    assert result.project.target_directory == target
    assert result.project.default_branch == "main"
    assert result.verification.required_files_present is True
    assert result.verification.git_repository is True
    assert result.verification.default_branch == "main"
    assert result.verification.initial_commit_present is True
    assert result.verification.python_package_present is True
    assert result.verification.smoke_test_present is True
    assert (target / "pyproject.toml").is_file()
    assert (target / "src" / "engineering_project" / "__init__.py").is_file()
    assert (target / "tests" / "test_smoke.py").is_file()


def test_bootstrap_delegates_to_public_sdk_exactly_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "delegated-project"
    calls = 0

    def counted_create(request):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        return create_standalone_project(request)

    monkeypatch.setattr(
        bootstrap_module,
        "create_standalone_project",
        counted_create,
    )

    result = bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=target,
            project_name="Delegated Project",
            project_description="Delegates exactly once.",
        )
    )

    assert calls == 1
    assert result.package_name == "delegated_project"


def test_bootstrap_rejects_unknown_profile_before_project_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "unknown-profile"

    def unexpected_create(request):  # type: ignore[no-untyped-def]
        raise AssertionError(f"creation must not be called: {request}")

    monkeypatch.setattr(
        bootstrap_module,
        "create_standalone_project",
        unexpected_create,
    )

    with pytest.raises(
        EngineeringBootstrapError,
        match="Unsupported engineering bootstrap profile",
    ):
        bootstrap_engineering_project(
            EngineeringBootstrapRequest(
                target_directory=target,
                project_name="Unknown Profile",
                project_description="Must fail before creation.",
                profile="PYTHON-ENGINEERING",
            )
        )

    assert not target.exists()


def test_bootstrap_preserves_existing_target_failure(tmp_path: Path) -> None:
    target = tmp_path / "existing-target"
    target.mkdir()
    (target / "existing.txt").write_text("existing")

    with pytest.raises(
        EngineeringBootstrapError,
        match="Target directory is not empty",
    ):
        bootstrap_engineering_project(
            EngineeringBootstrapRequest(
                target_directory=target,
                project_name="Existing Target",
                project_description="Must preserve SDK target safety.",
            )
        )


def test_bootstrap_preserves_nested_git_failure(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    target = tmp_path / "nested-target"

    with pytest.raises(
        EngineeringBootstrapError,
        match="inside an existing Git repository",
    ):
        bootstrap_engineering_project(
            EngineeringBootstrapRequest(
                target_directory=target,
                project_name="Nested Target",
                project_description="Must preserve SDK nested-Git safety.",
            )
        )

    assert not target.exists()


def test_bootstrap_supports_relative_destination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    target = Path("relative-project")

    result = bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=target,
            project_name="Relative Project",
            project_description="Portable relative destination.",
        )
    )

    assert result.project.target_directory == target
    assert (tmp_path / target / "README.md").is_file()
    generated_text = "\n".join(
        path.read_text()
        for path in (tmp_path / target).rglob("*")
        if path.is_file() and ".git" not in path.parts
    )
    assert str(tmp_path) not in generated_text


def test_bootstrap_initial_commit_contains_all_generated_files(tmp_path: Path) -> None:
    target = tmp_path / "committed-project"

    result = bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=target,
            project_name="Committed Project",
            project_description="All generated files are committed.",
        )
    )

    generated_files = {
        path.resolve().relative_to(target.resolve()).as_posix()
        for path in result.project.generated_files
    }
    assert generated_files == _committed_files(target)


def test_bootstrap_verification_failure_returns_no_success_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "verification-failure"

    def create_then_remove_smoke_test(request):  # type: ignore[no-untyped-def]
        project = create_standalone_project(request)
        (target / "tests" / "test_smoke.py").unlink()
        return project

    monkeypatch.setattr(
        bootstrap_module,
        "create_standalone_project",
        create_then_remove_smoke_test,
    )

    with pytest.raises(
        EngineeringBootstrapError,
        match="missing required files: tests/test_smoke.py",
    ):
        bootstrap_engineering_project(
            EngineeringBootstrapRequest(
                target_directory=target,
                project_name="Verification Failure",
                project_description="Verification must fail closed.",
            )
        )
