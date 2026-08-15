"""Command-line interface for standalone project templates and bootstrap."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from .engineering_bootstrap import (
    PYTHON_ENGINEERING_PROFILE,
    EngineeringBootstrapError,
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from .project_templates import (
    ProjectTemplateError,
    StandaloneProjectRequest,
    create_standalone_project,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-engineering")
    project = parser.add_subparsers(dest="command", required=True)
    actions = project.add_parser("project").add_subparsers(
        dest="action", required=True
    )

    create_project = actions.add_parser("create")
    create_project.add_argument("--name", required=True)
    create_project.add_argument("--destination", required=True)
    create_project.add_argument("--description", required=True)
    create_project.add_argument("--author")
    create_project.add_argument("--python-scaffold", action="store_true")

    bootstrap_project = actions.add_parser("bootstrap")
    bootstrap_project.add_argument("--name", required=True)
    bootstrap_project.add_argument("--destination", required=True)
    bootstrap_project.add_argument("--description", required=True)
    bootstrap_project.add_argument("--author")
    bootstrap_project.add_argument(
        "--profile",
        default=PYTHON_ENGINEERING_PROFILE,
    )
    return parser


def _create_project(args: argparse.Namespace) -> int:
    project = create_standalone_project(
        StandaloneProjectRequest(
            target_directory=Path(args.destination).resolve(),
            project_name=args.name,
            project_description=args.description,
            author=args.author,
            include_python_scaffold=args.python_scaffold,
        )
    )

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


def _bootstrap_project(args: argparse.Namespace) -> int:
    result = bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=Path(args.destination).resolve(),
            project_name=args.name,
            project_description=args.description,
            author=args.author,
            profile=args.profile,
        )
    )

    print(f"bootstrapped_project={result.project.target_directory}")
    print(f"project_name={args.name}")
    print(f"profile={result.profile}")
    print(f"package_name={result.package_name}")
    print(f"git_branch={result.verification.default_branch}")
    print("initial_commit=created")
    print("verification=passed")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.action == "bootstrap":
            return _bootstrap_project(args)
        return _create_project(args)
    except (
        EngineeringBootstrapError,
        ProjectTemplateError,
        subprocess.CalledProcessError,
        OSError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except Exception:
        print("error: unexpected internal failure", file=sys.stderr)
        return 3
