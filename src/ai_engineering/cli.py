"""Command-line interface for standalone project templates."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from .project_templates import (
    ProjectTemplateError,
    StandaloneProjectRequest,
    create_standalone_project,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-engineering")
    project = parser.add_subparsers(dest="command", required=True)
    create = project.add_parser("project").add_subparsers(dest="action", required=True)
    create_project = create.add_parser("create")
    create_project.add_argument("--name", required=True)
    create_project.add_argument("--destination", required=True)
    create_project.add_argument("--description", required=True)
    create_project.add_argument("--author")
    create_project.add_argument("--python-scaffold", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        project = create_standalone_project(
            StandaloneProjectRequest(
                target_directory=Path(args.destination).resolve(),
                project_name=args.name,
                project_description=args.description,
                author=args.author,
                include_python_scaffold=args.python_scaffold,
            )
        )
    except (ProjectTemplateError, subprocess.CalledProcessError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except Exception:
        print("error: unexpected internal failure", file=sys.stderr)
        return 3

    print(f"project_name={args.name}")
    print(f"created_project={project.target_directory}")
    print(f"project_path={project.target_directory}")
    print(f"git_branch={project.default_branch}")
    print("initial_commit=created")
    if args.python_scaffold:
        package_file = next(
            path
            for path in project.generated_files
            if path.name == "__init__.py" and path.parent.parent.name == "src"
        )
        print(f"package_name={package_file.parent.name}")
    return 0
