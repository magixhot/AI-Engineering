from __future__ import annotations

import importlib
import subprocess
import tomllib
from pathlib import Path

import pytest

from ai_engineering.project_templates import (
    ProjectTemplateError,
    ProjectTemplateGenerator,
    StandaloneProjectRequest,
    create_project_template,
    create_standalone_project,
)


def _generated_file_paths(target: Path) -> set[str]:
    return {
        path.relative_to(target).as_posix()
        for path in target.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(target).parts
    }


def test_generate_project_creates_required_documents(tmp_path: Path) -> None:
    target = tmp_path / "sample-project"
    metadata = {
        "PROJECT_NAME": "sample-project",
        "PROJECT_DESCRIPTION": "A sample generated project.",
    }

    generator = ProjectTemplateGenerator()
    generator.generate(target, metadata)

    for filename in generator.REQUIRED_DOCS:
        path = target / filename
        assert path.exists()
        content = path.read_text()
        assert "{{" not in content
        assert "## Document Metadata" in content
        assert "- Purpose:" in content
        assert "- Maintained by:" in content
        assert "- Created:" in content
        assert "- Mandatory sections:" in content
        assert "- Forbidden content:" in content

    readme_content = (target / "README.md").read_text()
    assert metadata["PROJECT_NAME"] in readme_content
    assert metadata["PROJECT_DESCRIPTION"] in readme_content


def test_generate_project_defaults_to_main_branch(tmp_path: Path) -> None:
    target = tmp_path / "branch-project"
    metadata = {
        "PROJECT_NAME": "branch-project",
        "PROJECT_DESCRIPTION": "Project with default branch.",
    }

    generator = ProjectTemplateGenerator()
    generator.generate(target, metadata)

    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "main"


def test_generate_project_does_not_create_docs_when_not_needed(tmp_path: Path) -> None:
    target = tmp_path / "minimal-project"
    metadata = {
        "PROJECT_NAME": "minimal-project",
        "PROJECT_DESCRIPTION": "A minimal generated project.",
    }

    generator = ProjectTemplateGenerator()
    generator.generate(target, metadata)

    assert not (target / "docs").exists()


def test_generate_project_creates_docs_when_provided(tmp_path: Path) -> None:
    target = tmp_path / "docs-project"
    metadata = {
        "PROJECT_NAME": "docs-project",
        "PROJECT_DESCRIPTION": "A generated project with docs.",
    }
    docs = {
        "feature-design.md": (
            "# Feature design for {{PROJECT_NAME}}\n\nDesc: {{PROJECT_DESCRIPTION}}\n"
        ),
    }

    generator = ProjectTemplateGenerator()
    generator.generate(target, metadata, docs=docs)

    docs_path = target / "docs" / "feature-design.md"
    assert docs_path.exists()
    content = docs_path.read_text()
    assert "{{" not in content
    assert "docs-project" in content
    assert "A generated project with docs." in content


def test_missing_required_placeholders_raises(tmp_path: Path) -> None:
    target = tmp_path / "missing-project"
    metadata = {
        "PROJECT_NAME": "missing-project",
    }

    generator = ProjectTemplateGenerator()

    with pytest.raises(
        ProjectTemplateError,
        match="Missing required metadata placeholders",
    ):
        generator.generate(target, metadata)


def test_unresolved_placeholder_in_optional_doc_raises(tmp_path: Path) -> None:
    target = tmp_path / "unresolved-project"
    metadata = {
        "PROJECT_NAME": "unresolved-project",
        "PROJECT_DESCRIPTION": "A project with unresolved placeholders.",
    }
    docs = {
        "feature-design.md": "# Feature design\n\nReference: {{UNKNOWN_PLACEHOLDER}}\n",
    }

    generator = ProjectTemplateGenerator()

    with pytest.raises(ProjectTemplateError, match="Unresolved placeholders found"):
        generator.generate(target, metadata, docs=docs)

    assert not target.exists()


def test_non_empty_target_directory_raises(tmp_path: Path) -> None:
    target = tmp_path / "existing-project"
    target.mkdir()
    (target / "README.md").write_text("existing")

    metadata = {
        "PROJECT_NAME": "existing-project",
        "PROJECT_DESCRIPTION": "Testing non-empty target.",
    }

    generator = ProjectTemplateGenerator()

    with pytest.raises(ProjectTemplateError, match="Target directory is not empty"):
        generator.generate(target, metadata)


def test_generate_fails_when_inside_existing_git_repo(tmp_path: Path) -> None:
    # Initialize a git repo at the tmp root
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    target = tmp_path / "nested-project"
    metadata = {
        "PROJECT_NAME": "nested-project",
        "PROJECT_DESCRIPTION": "Should fail inside parent git repo",
    }

    generator = ProjectTemplateGenerator()

    with pytest.raises(ProjectTemplateError, match="inside an existing Git repository"):
        generator.generate(target, metadata)

    assert not target.exists()


def test_optional_doc_filename_must_not_contain_windows_path_separator(
    tmp_path: Path,
) -> None:
    target = tmp_path / "invalid-doc-path"
    metadata = {
        "PROJECT_NAME": "invalid-doc-path",
        "PROJECT_DESCRIPTION": "Project with an invalid optional document path.",
    }

    generator = ProjectTemplateGenerator()

    with pytest.raises(ProjectTemplateError, match="Invalid docs filename"):
        generator.generate(target, metadata, docs={"..\\outside.md": "content"})

    assert not target.exists()


def test_generate_creates_initial_commit_with_only_generated_files(
    tmp_path: Path,
) -> None:
    target = tmp_path / "commit-project"
    metadata = {
        "PROJECT_NAME": "commit-project",
        "PROJECT_DESCRIPTION": "Project for testing commit content.",
    }

    generator = ProjectTemplateGenerator()
    generator.generate(target, metadata)

    # Check latest commit message
    res = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    )
    msg = res.stdout.strip()
    assert msg.startswith("Initial project scaffold:")
    assert "commit-project" in msg
    assert "Standalone template" in msg

    # Ensure the commit contains exactly the required docs
    res2 = subprocess.run(
        ["git", "ls-tree", "--name-only", "-r", "HEAD"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    )
    files = {line.strip() for line in res2.stdout.splitlines() if line.strip()}
    expected = set(generator.REQUIRED_DOCS)
    assert files == expected


def test_standalone_project_request_requires_core_fields() -> None:
    with pytest.raises(TypeError):
        StandaloneProjectRequest()  # type: ignore[call-arg]


def test_create_standalone_project_uses_optional_metadata_and_documents(
    tmp_path: Path,
) -> None:
    target = tmp_path / "typed-project"
    request = StandaloneProjectRequest(
        target_directory=target,
        project_name="typed-project",
        project_description="A typed SDK-0001 project.",
        project_id="SDK-0001",
        author="Template Author",
        created_date="2026-08-12",
        additional_documents={
            "provenance.md": (
                "{{PROJECT_ID}} | {{AUTHOR}} | {{CREATED_DATE}}\n"
            ),
        },
    )

    project = create_standalone_project(request)

    assert project.target_directory == target
    assert project.default_branch == "main"
    assert project.generated_files == (
        *(target / filename for filename in ProjectTemplateGenerator.REQUIRED_DOCS),
        target / "docs" / "provenance.md",
    )
    provenance = (target / "docs" / "provenance.md").read_text()
    assert provenance == "SDK-0001 | Template Author | 2026-08-12\n"
    assert "{{" not in provenance


def test_create_standalone_project_preserves_nested_git_protection(
    tmp_path: Path,
) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    request = StandaloneProjectRequest(
        target_directory=tmp_path / "nested-project",
        project_name="nested-project",
        project_description="Must not be generated in a parent Git repository.",
    )

    with pytest.raises(ProjectTemplateError, match="inside an existing Git repository"):
        create_standalone_project(request)

    assert not request.target_directory.exists()


def test_create_standalone_project_preserves_initial_commit_semantics(
    tmp_path: Path,
) -> None:
    target = tmp_path / "typed-commit-project"
    request = StandaloneProjectRequest(
        target_directory=target,
        project_name="typed-commit-project",
        project_description="A typed project with an initial commit.",
        additional_documents={"architecture.md": "# Architecture\n"},
    )

    create_standalone_project(request)

    commit_message = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert commit_message == (
        "Initial project scaffold: typed-commit-project (Standalone template)"
    )
    committed_files = subprocess.run(
        ["git", "ls-tree", "--name-only", "-r", "HEAD"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    assert set(committed_files) == {
        *ProjectTemplateGenerator.REQUIRED_DOCS,
        "docs/architecture.md",
    }


def test_create_project_template_remains_compatible(tmp_path: Path) -> None:
    target = tmp_path / "compatibility-project"
    metadata = {
        "PROJECT_NAME": "compatibility-project",
        "PROJECT_DESCRIPTION": "A mapping-based compatibility project.",
    }

    create_project_template(target, metadata)

    assert (target / "README.md").exists()
    assert not (target / "pyproject.toml").exists()


def test_scaffold_disabled_preserves_v1_output(tmp_path: Path) -> None:
    target = tmp_path / "v1-project"
    request = StandaloneProjectRequest(
        target_directory=target,
        project_name="v1-project",
        project_description="A V1-compatible project.",
    )

    project = create_standalone_project(request)

    assert project.generated_files == tuple(
        target / filename for filename in ProjectTemplateGenerator.REQUIRED_DOCS
    )
    assert _generated_file_paths(target) == set(ProjectTemplateGenerator.REQUIRED_DOCS)


def test_scaffold_enabled_generates_exact_required_file_set(tmp_path: Path) -> None:
    target = tmp_path / "scaffold-project"
    request = StandaloneProjectRequest(
        target_directory=target,
        project_name="Scaffold Project",
        project_description="A portable Python project.",
        include_python_scaffold=True,
    )

    project = create_standalone_project(request)

    expected_scaffold_files = {
        "pyproject.toml",
        ".gitignore",
        "src/scaffold_project/__init__.py",
        "tests/test_smoke.py",
    }
    assert _generated_file_paths(target) == {
        *ProjectTemplateGenerator.REQUIRED_DOCS,
        *expected_scaffold_files,
    }
    generated_files = {
        path.relative_to(target).as_posix() for path in project.generated_files
    }
    assert generated_files == {
        *ProjectTemplateGenerator.REQUIRED_DOCS,
        *expected_scaffold_files,
    }
    assert not (target / "LICENSE").exists()
    assert not (target / "src" / "scaffold_project" / "py.typed").exists()
    assert not (target / "tests" / "__init__.py").exists()


@pytest.mark.parametrize(
    ("project_name", "expected_package_name"),
    [
        ("My Sample-App", "my_sample_app"),
        ("123 Start", "project_123_start"),
        ("class", "project_class"),
        ("Hello!!!World", "hello_world"),
    ],
)
def test_package_name_derivation(
    project_name: str,
    expected_package_name: str,
) -> None:
    assert (
        ProjectTemplateGenerator._derive_package_name(project_name)
        == expected_package_name
    )


def test_scaffold_pyproject_matches_the_approved_contract(tmp_path: Path) -> None:
    target = tmp_path / "pyproject-project"
    request = StandaloneProjectRequest(
        target_directory=target,
        project_name="My Sample-App",
        project_description='A "portable" project.',
        author="Template Author",
        include_python_scaffold=True,
    )

    create_standalone_project(request)

    pyproject = tomllib.loads((target / "pyproject.toml").read_text())
    assert pyproject["build-system"] == {
        "requires": ["setuptools>=68"],
        "build-backend": "setuptools.build_meta",
    }
    assert pyproject["project"] == {
        "name": "my-sample-app",
        "version": "0.1.0",
        "description": 'A "portable" project.',
        "requires-python": ">=3.11",
        "dependencies": [],
        "authors": [{"name": "Template Author"}],
        "optional-dependencies": {
            "dev": ["pytest>=8", "ruff>=0.6", "mypy>=1.11"]
        },
    }
    assert pyproject["tool"] == {
        "pytest": {"ini_options": {"testpaths": ["tests"]}},
        "ruff": {
            "line-length": 88,
            "target-version": "py311",
            "lint": {"select": ["E", "F", "I"]},
        },
        "mypy": {
            "python_version": "3.11",
            "files": ["src", "tests"],
            "warn_unused_configs": True,
        },
    }


def test_generated_package_is_importable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "importable-project"
    request = StandaloneProjectRequest(
        target_directory=target,
        project_name="Importable Project",
        project_description="A project with an importable package.",
        include_python_scaffold=True,
    )

    create_standalone_project(request)
    monkeypatch.syspath_prepend(str(target / "src"))

    module = importlib.import_module("importable_project")
    assert module.__doc__ == "importable_project package."


def test_generated_smoke_test_is_valid(tmp_path: Path) -> None:
    target = tmp_path / "smoke-project"
    request = StandaloneProjectRequest(
        target_directory=target,
        project_name="Smoke Project",
        project_description="A project with a smoke test.",
        include_python_scaffold=True,
    )

    create_standalone_project(request)

    smoke_test = (target / "tests" / "test_smoke.py").read_text()
    compile(smoke_test, str(target / "tests" / "test_smoke.py"), "exec")
    assert 'import_module("smoke_project")' in smoke_test


def test_scaffold_initial_commit_includes_all_scaffold_files(tmp_path: Path) -> None:
    target = tmp_path / "commit-scaffold-project"
    request = StandaloneProjectRequest(
        target_directory=target,
        project_name="Commit Scaffold Project",
        project_description="A project with scaffold files in its initial commit.",
        include_python_scaffold=True,
    )

    create_standalone_project(request)

    committed_files = subprocess.run(
        ["git", "ls-tree", "--name-only", "-r", "HEAD"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    assert set(committed_files) == {
        *ProjectTemplateGenerator.REQUIRED_DOCS,
        "pyproject.toml",
        ".gitignore",
        "src/commit_scaffold_project/__init__.py",
        "tests/test_smoke.py",
    }


def test_scaffold_preserves_nested_git_protection(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    request = StandaloneProjectRequest(
        target_directory=tmp_path / "nested-scaffold-project",
        project_name="Nested Scaffold Project",
        project_description="Must not be generated in a parent Git repository.",
        include_python_scaffold=True,
    )

    with pytest.raises(ProjectTemplateError, match="inside an existing Git repository"):
        create_standalone_project(request)

    assert not request.target_directory.exists()


def test_scaffold_rejects_invalid_package_names_and_options(tmp_path: Path) -> None:
    invalid_name_request = StandaloneProjectRequest(
        target_directory=tmp_path / "invalid-name-project",
        project_name="!!!",
        project_description="A project with an invalid package name.",
        include_python_scaffold=True,
    )
    invalid_option_request = StandaloneProjectRequest(
        target_directory=tmp_path / "invalid-option-project",
        project_name="Invalid Option Project",
        project_description="A project with an invalid scaffold option.",
        include_python_scaffold="yes",  # type: ignore[arg-type]
    )

    with pytest.raises(ProjectTemplateError, match="Invalid package name"):
        create_standalone_project(invalid_name_request)
    with pytest.raises(ProjectTemplateError, match="must be a boolean"):
        create_standalone_project(invalid_option_request)

    assert not invalid_name_request.target_directory.exists()
    assert not invalid_option_request.target_directory.exists()


def test_scaffold_request_default_preserves_typed_api_compatibility(
    tmp_path: Path,
) -> None:
    target = tmp_path / "typed-api-project"
    request = StandaloneProjectRequest(
        target_directory=target,
        project_name="Typed API Project",
        project_description="A project using the existing typed API.",
    )

    project = create_standalone_project(request)

    assert request.include_python_scaffold is False
    assert project.generated_files == tuple(
        target / filename for filename in ProjectTemplateGenerator.REQUIRED_DOCS
    )
