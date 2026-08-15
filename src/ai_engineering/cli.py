"""Command-line interface for project creation, bootstrap, and documentation sync."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from .documentation_apply import apply_documentation_sync
from .documentation_sync import (
    DocumentationDriftReport,
    DocumentationSyncError,
    detect_documentation_drift,
    plan_documentation_sync,
)
from .engineering_bootstrap import (
    PYTHON_ENGINEERING_PROFILE,
    EngineeringBootstrapError,
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from .project_inspection import (
    ProjectInspectionError,
    ProjectInspectionRequest,
    inspect_project_state,
)
from .project_templates import (
    ProjectTemplateError,
    StandaloneProjectRequest,
    create_standalone_project,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-engineering")
    commands = parser.add_subparsers(dest="command", required=True)
    project_parser = commands.add_parser("project")
    actions = project_parser.add_subparsers(dest="action", required=True)

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

    docs_project = actions.add_parser("docs")
    docs_actions = docs_project.add_subparsers(dest="docs_action", required=True)
    for action in ("check", "plan", "apply"):
        docs_command = docs_actions.add_parser(action)
        docs_command.add_argument("--project", required=True)

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


def _documentation_report(project_root: Path) -> DocumentationDriftReport:
    snapshot = inspect_project_state(ProjectInspectionRequest(project_root))
    return detect_documentation_drift(snapshot)


def _manual_review_count(report: DocumentationDriftReport) -> int:
    return sum(
        item.category == "manual_review_required" for item in report.items
    )


def _docs_check(project_root: Path) -> int:
    report = _documentation_report(project_root)
    manual_review_count = _manual_review_count(report)

    print(f"project={report.project.project_root}")
    print(f"drift_count={len(report.items)}")
    print(f"manual_review_count={manual_review_count}")
    for item in report.items:
        print(f"drift={item.document}:{item.category}")
    print(f"status={'drift' if report.items else 'clean'}")
    return 1 if report.items else 0


def _docs_plan(project_root: Path) -> int:
    report = _documentation_report(project_root)
    plan = plan_documentation_sync(report)
    manual_review_count = _manual_review_count(report)
    if manual_review_count:
        status = "manual_review"
    elif plan.updates:
        status = "ready"
    else:
        status = "clean"

    print(f"project={report.project.project_root}")
    print(f"update_count={len(plan.updates)}")
    print(f"manual_review_count={manual_review_count}")
    for update in plan.updates:
        print(f"update={update.document}:{update.original_sha256}")
    print(f"status={status}")
    return 1 if manual_review_count else 0


def _docs_apply(project_root: Path) -> int:
    report = _documentation_report(project_root)
    manual_review_count = _manual_review_count(report)
    if manual_review_count:
        raise DocumentationSyncError(
            "Manual review required before documentation apply"
        )

    plan = plan_documentation_sync(report)
    result = apply_documentation_sync(plan)
    print(f"project={result.project_root}")
    print(f"changed_count={len(result.changed_documents)}")
    for document in result.changed_documents:
        print(f"changed_document={document}")
    print("verification=passed")
    return 0


def _project_docs(args: argparse.Namespace) -> int:
    project_root = Path(args.project).resolve()
    if args.docs_action == "check":
        return _docs_check(project_root)
    if args.docs_action == "plan":
        return _docs_plan(project_root)
    return _docs_apply(project_root)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.action == "bootstrap":
            return _bootstrap_project(args)
        if args.action == "docs":
            return _project_docs(args)
        return _create_project(args)
    except (
        DocumentationSyncError,
        EngineeringBootstrapError,
        ProjectInspectionError,
        ProjectTemplateError,
        subprocess.CalledProcessError,
        OSError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except Exception:
        print("error: unexpected internal failure", file=sys.stderr)
        return 3
