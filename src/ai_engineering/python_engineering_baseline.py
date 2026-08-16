from __future__ import annotations

from typing import Mapping

from .project_templates import (
    ProjectTemplateGenerator,
    StandaloneProject,
    StandaloneProjectRequest,
)

PYTHON_ENGINEERING_PROFILE = "python-engineering"
PYTHON_ENGINEERING_V2_BASELINE = "python-engineering-v2"
PYTHON_ENGINEERING_IDENTITY_PATH = ".ai-engineering.toml"

PYTHON_ENGINEERING_V2_IDENTITY = (
    "schema = 1\n"
    'profile = "python-engineering"\n'
    'baseline = "python-engineering-v2"\n'
)

PYTHON_ENGINEERING_V2_GITIGNORE = (
    "__pycache__/\n"
    "*.py[cod]\n"
    ".venv/\n"
    "venv/\n"
    ".coverage\n"
    "htmlcov/\n"
    "build/\n"
    "dist/\n"
    "*.egg-info/\n"
    ".pytest_cache/\n"
    ".mypy_cache/\n"
    ".ruff_cache/\n"
    ".idea/\n"
    ".vscode/\n"
)


class _PythonEngineeringV2Generator(ProjectTemplateGenerator):
    """Bounded AUTO-0005 profile augmentation over the SDK generator."""

    def _build_python_scaffold(self, metadata: Mapping[str, str]) -> dict[str, str]:
        files = super()._build_python_scaffold(metadata)
        files[".gitignore"] = PYTHON_ENGINEERING_V2_GITIGNORE
        files[PYTHON_ENGINEERING_IDENTITY_PATH] = PYTHON_ENGINEERING_V2_IDENTITY
        return files


def create_python_engineering_v2_project(
    request: StandaloneProjectRequest,
) -> StandaloneProject:
    """Create one python-engineering V2 project in a single initial commit."""

    if not request.include_python_scaffold:
        raise ValueError("python-engineering V2 requires the Python scaffold")

    metadata = {
        "PROJECT_NAME": request.project_name,
        "PROJECT_DESCRIPTION": request.project_description,
    }
    optional_metadata = {
        "PROJECT_ID": request.project_id,
        "AUTHOR": request.author,
        "CREATED_DATE": request.created_date,
    }
    metadata.update(
        {
            key: value
            for key, value in optional_metadata.items()
            if value is not None
        }
    )

    additional_documents = dict(request.additional_documents)
    generator = _PythonEngineeringV2Generator()
    generator.generate(
        request.target_directory,
        metadata,
        docs=additional_documents,
        include_python_scaffold=True,
    )

    generated_files = tuple(
        request.target_directory / filename for filename in generator.REQUIRED_DOCS
    ) + tuple(
        request.target_directory / "docs" / filename
        for filename in sorted(additional_documents)
    )
    generated_files += tuple(
        request.target_directory / filename
        for filename in generator._build_python_scaffold(metadata)
    )

    return StandaloneProject(
        target_directory=request.target_directory,
        generated_files=generated_files,
    )
