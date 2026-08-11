from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Dict, Mapping, Optional

from .workspace.service import WorkspaceService

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([A-Z0-9_]+)\s*}}")


class ProjectTemplateError(Exception):
    pass


class ProjectTemplateGenerator:
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

    TEMPLATE_CONTENTS: Dict[str, str] = {
        "README.md": (
            "# {{PROJECT_NAME}}\n"
            "\n"
            "{{PROJECT_DESCRIPTION}}\n"
            "\n"
            "## Purpose\n"
            "This project is generated from the SDK-0001 standalone template.\n"
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
            "\n"
            "## Sprint 1 — Project Implementation\n"
            "- Add source and tests after documentation approval.\n"
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
        ),
    }

    def __init__(self, workspace_service: WorkspaceService | None = None) -> None:
        self._workspace_service = workspace_service or WorkspaceService()

    def generate(
        self,
        target_directory: Path,
        metadata: Mapping[str, str],
        docs: Optional[Dict[str, str]] = None,
    ) -> None:
        self._ensure_required_metadata(metadata)
        docs = docs or {}
        self._validate_target_directory(target_directory)
        self._create_project_directory(target_directory)
        self._write_required_documents(target_directory, metadata)
        self._write_optional_docs(target_directory, metadata, docs)
        self._initialize_git_repository(target_directory)

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

    def _create_project_directory(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def _write_required_documents(
        self,
        target_directory: Path,
        metadata: Mapping[str, str],
    ) -> None:
        for filename in self.REQUIRED_DOCS:
            content = self.TEMPLATE_CONTENTS[filename]
            rendered = self._render_template(content, metadata)
            self._write_file(target_directory / filename, rendered)

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
            if "/" in filename or filename.startswith("."):
                raise ProjectTemplateError(f"Invalid docs filename: {filename}")
            rendered = self._render_template(content, metadata)
            self._write_file(docs_dir / filename, rendered)

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

    def _initialize_git_repository(self, target_directory: Path) -> None:
        # Prevent initializing a git repo inside an existing repository
        # by checking parent directories for a .git entry.
        def _check_parent_for_git(path: Path) -> bool:
            for parent in path.resolve().parents:
                if (parent / ".git").exists():
                    return True
            return False

        if _check_parent_for_git(target_directory):
            raise ProjectTemplateError(
                "Target directory is inside an existing Git repository"
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
    generator = ProjectTemplateGenerator()
    generator.generate(target_directory, metadata, docs)
