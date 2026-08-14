from __future__ import annotations

import json
import keyword
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping, Optional

from .workspace.service import WorkspaceService

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([A-Z0-9_]+)\s*}}")


class ProjectTemplateError(Exception):
    pass


@dataclass(frozen=True)
class StandaloneProjectRequest:
    """Typed input for a standalone document-first project generation."""

    target_directory: Path
    project_name: str
    project_description: str
    project_id: str | None = None
    author: str | None = None
    created_date: str | None = None
    additional_documents: Mapping[str, str] = field(default_factory=dict)
    include_python_scaffold: bool = False


@dataclass(frozen=True)
class StandaloneProject:
    """Result of generating a standalone document-first project."""

    target_directory: Path
    generated_files: tuple[Path, ...]
    default_branch: str = "main"


class ProjectTemplateGenerator:
    """Implementation layer for the SDK-0001 document-first template."""

    REQUIRED_PLACEHOLDERS = {"PROJECT_NAME", "PROJECT_DESCRIPTION"}
    OPTIONAL_PLACEHOLDERS = {"PROJECT_ID", "AUTHOR", "CREATED_DATE"}
    ALLOWED_PLACEHOLDERS = REQUIRED_PLACEHOLDERS | OPTIONAL_PLACEHOLDERS

    REQUIRED_DOCS = [
        "README.md",
        "AI_CHAT_START.md",
        "PROJECT_CONTEXT.md",
        "PROJECT_MAP.md",
        "CURRENT_STATUS.md",
        "ROADMAP.md",
        "DECISIONS.md",
        "CODING_STANDARDS.md",
        "MASTER_INDEX.md",
    ]

    DOCUMENT_METADATA: Dict[str, tuple[str, str, str]] = {
        "README.md": (
            "Project overview, scope, and contributor guidance.",
            "project name, purpose and scope, bootstrap guidance, documentation links",
            "implementation detail beyond the architecture summary",
        ),
        "AI_CHAT_START.md": (
            "Bootstrap context for a new project chat session.",
            "document purpose, bootstrap order, core documents, current status, "
            "continuation guidance",
            "AI-Engineering operational history or code-generation instructions",
        ),
        "PROJECT_CONTEXT.md": (
            "Project vision, objectives, and engineering principles.",
            "project purpose, vision, initial objectives, engineering principles",
            "implementation task lists that belong in ROADMAP.md",
        ),
        "PROJECT_MAP.md": (
            "Repository structure and architecture boundaries.",
            "repository layout, architecture overview, development phases",
            "detailed implementation plans or APIs",
        ),
        "CURRENT_STATUS.md": (
            "Current phase, completed work, and immediate next steps.",
            "status, current phase, completed items, in-progress items, next steps",
            "speculative milestones without current relevance",
        ),
        "ROADMAP.md": (
            "Planned project phases and deliverables.",
            "roadmap structure, phase goals, planned deliverables, phase status",
            "implementation-only task checklists",
        ),
        "DECISIONS.md": (
            "Accepted engineering decisions and policies.",
            "decision ID, title, status, decision statement, rationale",
            "transient discussion notes or unresolved debates",
        ),
        "CODING_STANDARDS.md": (
            "Code and design conventions for the project.",
            "general principles, architecture guidance, naming, testing and "
            "documentation",
            "project-specific implementation details",
        ),
        "MASTER_INDEX.md": (
            "Document index and project overview.",
            "document table, project status, source tree outline, current priority",
            "outdated document listings or marketing content",
        ),
    }

    TEMPLATE_CONTENTS: Dict[str, str] = {
        "README.md": (
            "# {{PROJECT_NAME}}\n"
            "\n"
            "{{PROJECT_DESCRIPTION}}\n"
            "\n"
            "## Purpose\n"
            "This project is generated from the SDK-0001 standalone template.\n"
            "\n"
            "## Scope\n"
            "The initial scope is a documentation-first project foundation.\n"
            "\n"
            "## Bootstrap\n"
            "Start by reading `AI_CHAT_START.md` and then follow the project\n"
            "documentation.\n"
            "\n"
            "## Documentation\n"
            "- `AI_CHAT_START.md`\n"
            "- `PROJECT_CONTEXT.md`\n"
            "- `PROJECT_MAP.md`\n"
            "- `CURRENT_STATUS.md`\n"
            "- `ROADMAP.md`\n"
            "- `DECISIONS.md`\n"
            "- `CODING_STANDARDS.md`\n"
            "- `MASTER_INDEX.md`\n"
        ),
        "AI_CHAT_START.md": (
            "# AI_CHAT_START\n"
            "\n"
            "This document bootstraps chat sessions for the generated project.\n"
            "\n"
            "## Bootstrap order\n"
            "1. README.md\n"
            "2. PROJECT_CONTEXT.md\n"
            "3. PROJECT_MAP.md\n"
            "4. CURRENT_STATUS.md\n"
            "5. ROADMAP.md\n"
            "6. DECISIONS.md\n"
            "7. CODING_STANDARDS.md\n"
            "8. MASTER_INDEX.md\n"
            "\n"
            "## Core Project Documents\n"
            "The bootstrap order lists the required project documents.\n"
            "\n"
            "## Current Project Status\n"
            "The generated project begins in the template generation foundation "
            "phase.\n"
            "\n"
            "## Project context\n"
            "The generated project is `{{PROJECT_NAME}}` and should be understood\n"
            "through the project documents above.\n"
            "\n"
            "Continue from the current project status and roadmap once these\n"
            "documents are read.\n"
        ),
        "PROJECT_CONTEXT.md": (
            "# PROJECT_CONTEXT\n"
            "\n"
            "## Project Purpose\n"
            "Provide a standalone generated project skeleton for `{{PROJECT_NAME}}`.\n"
            "\n"
            "## Vision\n"
            "Enable consistent engineering documentation and project bootstrap\n"
            "practices.\n"
            "\n"
            "## Initial Objectives\n"
            "- Establish project documentation.\n"
            "- Preserve architecture and generation conventions.\n"
            "\n"
            "## Engineering Principles\n"
            "- Documentation before implementation.\n"
            "- Small, testable increments.\n"
            "- Clear public API boundaries.\n"
        ),
        "PROJECT_MAP.md": (
            "# PROJECT_MAP\n"
            "\n"
            "## Repository Structure\n"
            "- README.md\n"
            "- AI_CHAT_START.md\n"
            "- PROJECT_CONTEXT.md\n"
            "- PROJECT_MAP.md\n"
            "- CURRENT_STATUS.md\n"
            "- ROADMAP.md\n"
            "- DECISIONS.md\n"
            "- CODING_STANDARDS.md\n"
            "- MASTER_INDEX.md\n"
            "\n"
            "## Architecture Overview\n"
            "The generated project is intentionally minimal.\n"
            "\n"
            "## Development Phases\n"
            "- Documentation foundation\n"
            "- Template review\n"
            "- Implementation\n"
        ),
        "CURRENT_STATUS.md": (
            "# CURRENT_STATUS\n"
            "\n"
            "## Status\n"
            "ACTIVE\n"
            "\n"
            "## Current Phase\n"
            "Template generation foundation.\n"
            "\n"
            "## Completed\n"
            "- Project skeleton created.\n"
            "\n"
            "## In Progress\n"
            "- Project documentation review.\n"
            "\n"
            "## Next Steps\n"
            "- Validate generated project structure.\n"
        ),
        "ROADMAP.md": (
            "# ROADMAP\n"
            "\n"
            "## Project Roadmap\n"
            "\n"
            "## Sprint 0 — Documentation Foundation\n"
            "- Complete required project documents.\n"
            "- Status: Active\n"
            "\n"
            "## Sprint 1 — Project Implementation\n"
            "- Add source and tests after documentation approval.\n"
            "- Status: Planned\n"
        ),
        "DECISIONS.md": (
            "# DECISIONS\n"
            "\n"
            "## DEC-0001\n"
            "### Title\n"
            "Generated project documentation foundation.\n"
            "\n"
            "### Status\n"
            "ACCEPTED\n"
            "\n"
            "### Decision\n"
            "The project is generated with a consistent documentation set and may\n"
            "extend with additional docs only when necessary.\n"
        ),
        "CODING_STANDARDS.md": (
            "# CODING_STANDARDS\n"
            "\n"
            "## General Principles\n"
            "- Readability over cleverness.\n"
            "- Simple, focused modules.\n"
            "\n"
            "## Naming\n"
            "- Use descriptive names.\n"
            "- Use lowercase and underscore separation for Python packages.\n"
            "\n"
            "## Architecture Guidance\n"
            "- Keep modules focused and dependencies explicit.\n"
            "\n"
            "## Testing and Documentation\n"
            "- Add tests for observable behavior.\n"
            "- Update documentation with relevant changes.\n"
        ),
        "MASTER_INDEX.md": (
            "# MASTER_INDEX\n"
            "\n"
            "## Project Documents\n"
            "- README.md | Project overview | Active\n"
            "- AI_CHAT_START.md | Chat bootstrap and context recovery | Active\n"
            "- PROJECT_CONTEXT.md | Project vision and objectives | Active\n"
            "- PROJECT_MAP.md | Repository structure | Active\n"
            "- CURRENT_STATUS.md | Current phase and status | Active\n"
            "- ROADMAP.md | Development roadmap | Active\n"
            "- DECISIONS.md | Engineering decisions | Active\n"
            "- CODING_STANDARDS.md | Coding conventions | Active\n"
            "- MASTER_INDEX.md | Documentation index | Active\n"
            "\n"
            "## Current Status\n"
            "Template generation foundation is active.\n"
            "\n"
            "## Source Tree Outline\n"
            "- Project documentation is at the repository root.\n"
            "- Optional additional documents are in docs/.\n"
            "\n"
            "## Current Priority\n"
            "Validate and extend the generated project deliberately.\n"
        ),
    }

    def __init__(self, workspace_service: WorkspaceService | None = None) -> None:
        self._workspace_service = workspace_service or WorkspaceService()

    def generate(
        self,
        target_directory: Path,
        metadata: Mapping[str, str],
        docs: Optional[Dict[str, str]] = None,
        include_python_scaffold: bool = False,
    ) -> None:
        self._ensure_required_metadata(metadata)
        docs = docs or {}
        self._validate_scaffold_option(include_python_scaffold)
        self._validate_target_directory(target_directory)
        self._ensure_not_inside_git_repository(target_directory)
        self._validate_optional_docs(docs, metadata)
        scaffold_files = (
            self._build_python_scaffold(metadata) if include_python_scaffold else {}
        )
        self._validate_generated_file_paths(
            target_directory,
            docs,
            scaffold_files,
        )
        self._create_project_directory(target_directory)
        self._write_required_documents(target_directory, metadata)
        self._write_optional_docs(target_directory, metadata, docs)
        self._write_scaffold_files(target_directory, scaffold_files)
        self._initialize_git_repository(target_directory, scaffold_files)

    def _ensure_required_metadata(self, metadata: Mapping[str, str]) -> None:
        missing = [
            name for name in self.REQUIRED_PLACEHOLDERS if not metadata.get(name)
        ]
        if missing:
            raise ProjectTemplateError(
                f"Missing required metadata placeholders: {', '.join(missing)}"
            )

    def _validate_target_directory(self, target_directory: Path) -> None:
        if target_directory.exists():
            if not target_directory.is_dir():
                raise ProjectTemplateError(
                    f"Target exists and is not a directory: {target_directory}"
                )
            if any(target_directory.iterdir()):
                raise ProjectTemplateError(
                    f"Target directory is not empty: {target_directory}"
                )

    def _validate_scaffold_option(self, include_python_scaffold: bool) -> None:
        if not isinstance(include_python_scaffold, bool):
            raise ProjectTemplateError("include_python_scaffold must be a boolean")

    @staticmethod
    def _derive_package_name(project_name: str) -> str:
        normalized = project_name.strip().lower()
        normalized = re.sub(r"[ -]+", "_", normalized)
        normalized = re.sub(r"[^a-z0-9_]", "_", normalized)
        normalized = re.sub(r"_+", "_", normalized).strip("_")

        if normalized and normalized[0].isdigit():
            normalized = f"project_{normalized}"
        if keyword.iskeyword(normalized):
            normalized = f"project_{normalized}"

        if (
            not normalized
            or not normalized.isascii()
            or not normalized.isidentifier()
            or keyword.iskeyword(normalized)
        ):
            raise ProjectTemplateError(
                f"Invalid package name derived from project name: {project_name!r}"
            )
        return normalized

    def _build_python_scaffold(self, metadata: Mapping[str, str]) -> dict[str, str]:
        package_name = self._derive_package_name(metadata["PROJECT_NAME"])
        distribution_name = package_name.replace("_", "-")
        author = metadata.get("AUTHOR")
        authors = (
            f"authors = [{{ name = {json.dumps(author)} }}]\n" if author else ""
        )
        pyproject = (
            "[build-system]\n"
            'requires = ["setuptools>=68"]\n'
            'build-backend = "setuptools.build_meta"\n'
            "\n"
            "[project]\n"
            f"name = {json.dumps(distribution_name)}\n"
            'version = "0.1.0"\n'
            f"description = {json.dumps(metadata['PROJECT_DESCRIPTION'])}\n"
            'requires-python = ">=3.11"\n'
            "dependencies = []\n"
            f"{authors}"
            "\n"
            "[project.optional-dependencies]\n"
            'dev = ["pytest>=8", "ruff>=0.6", "mypy>=1.11"]\n'
            "\n"
            "[tool.pytest.ini_options]\n"
            'testpaths = ["tests"]\n'
            "\n"
            "[tool.ruff]\n"
            "line-length = 88\n"
            'target-version = "py311"\n'
            "\n"
            "[tool.ruff.lint]\n"
            'select = ["E", "F", "I"]\n'
            "\n"
            "[tool.mypy]\n"
            'python_version = "3.11"\n'
            'files = ["src", "tests"]\n'
            "warn_unused_configs = true\n"
        )
        return {
            "pyproject.toml": pyproject,
            ".gitignore": (
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
            ),
            f"src/{package_name}/__init__.py": f'"""{package_name} package."""\n',
            "tests/test_smoke.py": (
                '"""Smoke test for the generated package."""\n'
                "\n"
                "from importlib import import_module\n"
                "\n"
                "\n"
                "def test_package_is_importable() -> None:\n"
                f'    module = import_module("{package_name}")\n'
                "    assert module is not None\n"
            ),
        }

    def _validate_generated_file_paths(
        self,
        target_directory: Path,
        docs: Mapping[str, str],
        scaffold_files: Mapping[str, str],
    ) -> None:
        generated_paths = [
            *self.REQUIRED_DOCS,
            *(str(Path("docs") / filename) for filename in docs),
            *scaffold_files,
        ]
        normalized_paths = [
            Path(path).as_posix().casefold() for path in generated_paths
        ]
        if len(normalized_paths) != len(set(normalized_paths)):
            raise ProjectTemplateError("Generated file paths must not collide")
        for path in generated_paths:
            if (target_directory / path).exists():
                raise ProjectTemplateError(f"Generated file already exists: {path}")

    def _create_project_directory(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def _write_required_documents(
        self,
        target_directory: Path,
        metadata: Mapping[str, str],
    ) -> None:
        for filename in self.REQUIRED_DOCS:
            content = self.TEMPLATE_CONTENTS[filename]
            title, separator, body = content.partition("\n")
            content = (
                f"{title}\n\n{self._document_metadata(filename)}{body}"
                if separator
                else f"{title}\n\n{self._document_metadata(filename)}"
            )
            rendered = self._render_template(content, metadata)
            self._write_file(target_directory / filename, rendered)

    def _document_metadata(self, filename: str) -> str:
        purpose, sections, forbidden_content = self.DOCUMENT_METADATA[filename]
        return (
            "## Document Metadata\n"
            f"- Purpose: {purpose}\n"
            "- Maintained by: project owner or maintainer.\n"
            "- Created: at project generation time.\n"
            f"- Mandatory sections: {sections}.\n"
            f"- Forbidden content: {forbidden_content}.\n"
            "\n"
        )

    def _write_optional_docs(
        self,
        target_directory: Path,
        metadata: Mapping[str, str],
        docs: Dict[str, str],
    ) -> None:
        if not docs:
            return

        docs_dir = target_directory / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        for filename, content in docs.items():
            rendered = self._render_template(content, metadata)
            self._write_file(docs_dir / filename, rendered)

    def _write_scaffold_files(
        self,
        target_directory: Path,
        scaffold_files: Mapping[str, str],
    ) -> None:
        for relative_path, content in scaffold_files.items():
            path = target_directory / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            self._write_file(path, content)

    def _validate_optional_docs(
        self,
        docs: Mapping[str, str],
        metadata: Mapping[str, str],
    ) -> None:
        for filename, content in docs.items():
            if (
                not filename
                or "/" in filename
                or "\\" in filename
                or filename.startswith(".")
                or Path(filename).name != filename
            ):
                raise ProjectTemplateError(f"Invalid docs filename: {filename}")
            self._render_template(content, metadata)

    def _render_template(
        self,
        content: str,
        metadata: Mapping[str, str],
    ) -> str:
        # Replace placeholders allowing optional spaces inside the braces.
        # Use the compiled PLACEHOLDER_PATTERN to find occurrences like {{ KEY }}.
        def _repl(m) -> str:
            key = m.group(1)
            val = metadata.get(key)
            if key in self.ALLOWED_PLACEHOLDERS and val is not None:
                return str(val)
            # leave unresolved placeholder text intact for later detection
            return str(m.group(0))

        rendered = PLACEHOLDER_PATTERN.sub(_repl, content)
        unresolved = self._find_unresolved_placeholders(rendered)
        if unresolved:
            raise ProjectTemplateError(
                f"Unresolved placeholders found: {', '.join(sorted(unresolved))}"
            )
        return rendered

    def _find_unresolved_placeholders(self, content: str) -> set[str]:
        return {match.group(1) for match in PLACEHOLDER_PATTERN.finditer(content)}

    def _write_file(self, path: Path, content: str) -> None:
        if path.exists():
            raise ProjectTemplateError(f"File already exists: {path}")
        self._workspace_service.write_file(path, content)

    def _ensure_not_inside_git_repository(self, target_directory: Path) -> None:
        for parent in target_directory.resolve().parents:
            if (parent / ".git").exists():
                raise ProjectTemplateError(
                    "Target directory is inside an existing Git repository"
                )

    def _initialize_git_repository(
        self,
        target_directory: Path,
        scaffold_files: Mapping[str, str],
    ) -> None:
        if not target_directory.exists():
            raise ProjectTemplateError(
                f"Target directory does not exist: {target_directory}"
            )

        # Initialize git and ensure default branch is 'main'.
        try:
            subprocess.run(
                ["git", "init", "--initial-branch=main"],
                cwd=target_directory,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError:
            # fallback for older Git versions
            subprocess.run(
                ["git", "init"],
                cwd=target_directory,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "branch", "-M", "main"],
                cwd=target_directory,
                check=True,
                capture_output=True,
                text=True,
            )

        # Stage only the generated files (do not use `git add .`).
        # Build relative paths for required docs and any generated docs.
        to_add: list[str] = []
        for filename in self.REQUIRED_DOCS:
            to_add.append(filename)

        docs_dir = target_directory / "docs"
        if docs_dir.exists() and docs_dir.is_dir():
            for p in sorted(docs_dir.iterdir()):
                if p.is_file():
                    # add relative path like docs/filename
                    to_add.append(str(Path("docs") / p.name))
        to_add.extend(scaffold_files)

        if to_add:
            subprocess.run(
                ["git", "add", "--"] + to_add,
                cwd=target_directory,
                check=True,
                capture_output=True,
                text=True,
            )

            # Create initial commit with the specified message
            project_name = None
            # try to get project name from README or metadata fallback
            readme = target_directory / "README.md"
            if readme.exists():
                try:
                    first_line = readme.read_text()[:512].splitlines()[0]
                    # assume first header contains the project name
                    if first_line.startswith("#"):
                        project_name = first_line.lstrip("# ").strip()
                except Exception:
                    project_name = None

            commit_message = (
                f"Initial project scaffold: {project_name or ''} (Standalone template)"
            )

            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=target_directory,
                check=True,
                capture_output=True,
                text=True,
            )


def create_project_template(
    target_directory: Path,
    metadata: Mapping[str, str],
    docs: Optional[Dict[str, str]] = None,
) -> None:
    """Compatibility-level API for the original mapping-based generator call."""

    generator = ProjectTemplateGenerator()
    generator.generate(target_directory, metadata, docs)


def create_standalone_project(
    request: StandaloneProjectRequest,
) -> StandaloneProject:
    """Create a standalone SDK-0001 document-first project from typed input."""

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
    generator = ProjectTemplateGenerator()
    generator.generate(
        request.target_directory,
        metadata,
        docs=additional_documents,
        include_python_scaffold=request.include_python_scaffold,
    )

    generated_files = tuple(
        request.target_directory / filename
        for filename in generator.REQUIRED_DOCS
    ) + tuple(
        request.target_directory / "docs" / filename
        for filename in sorted(additional_documents)
    )
    if request.include_python_scaffold:
        generated_files += tuple(
            request.target_directory / filename
            for filename in generator._build_python_scaffold(metadata)
        )
    return StandaloneProject(
        target_directory=request.target_directory,
        generated_files=generated_files,
    )
