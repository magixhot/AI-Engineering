"""Command-line interface for project engineering workflows."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from .documentation_apply import apply_documentation_sync
from .documentation_ownership import (
    DocumentationOwnershipError,
    apply_documentation_ownership_initialization,
    plan_documentation_ownership_initialization,
)
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
from .project_health import ProjectHealthReport, audit_project_health
from .project_inspection import (
    ProjectInspectionError,
    ProjectInspectionRequest,
    inspect_project_state,
)
from .project_migration import (
    DEFAULT_MIGRATION_REGISTRY,
    ProjectMigrationError,
    ProjectMigrationPlan,
    ProjectMigrationRequest,
    plan_project_migration,
)
from .project_migration_apply import (
    ProjectMigrationApplyError,
    apply_project_migration,
)
from .project_reconciliation_cli import run_reconciliation_plan
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

    health_project = actions.add_parser("health")
    health_project.add_argument("--project", required=True)

    reconcile_project = actions.add_parser("reconcile")
    reconcile_actions = reconcile_project.add_subparsers(
        dest="reconcile_action",
        required=True,
    )
    reconcile_plan = reconcile_actions.add_parser("plan")
    reconcile_plan.add_argument("--project", required=True)

    docs_project = actions.add_parser("docs")
    docs_actions = docs_project.add_subparsers(dest="docs_action", required=True)
    for action in ("check", "plan", "apply"):
        docs_command = docs_actions.add_parser(action)
        docs_command.add_argument("--project", required=True)

    ownership_project = docs_actions.add_parser("ownership")
    ownership_actions = ownership_project.add_subparsers(
        dest="ownership_action",
        required=True,
    )
    for action in ("check", "plan", "apply"):
        ownership_command = ownership_actions.add_parser(action)
        ownership_command.add_argument("--project", required=True)

    migrate_project = actions.add_parser("migrate")
    migrate_actions = migrate_project.add_subparsers(
        dest="migrate_action",
        required=True,
    )
    for action in ("check", "plan", "apply"):
        migrate_command = migrate_actions.add_parser(action)
        migrate_command.add_argument("--project", required=True)
        migrate_command.add_argument("--migration", required=True)

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


def _single_line(value: str) -> str:
    return " ".join(value.replace("\r", "\n").splitlines()).strip()


def _print_health_report(report: ProjectHealthReport) -> None:
    identity = report.identity
    print(f"project={report.project_root}")
    print(f"overall={report.overall_state}")
    print(f"identity={identity.profile if identity is not None else 'unsupported'}")
    print(f"baseline={identity.baseline if identity is not None else 'unknown'}")
    print(f"git={report.git_state}")
    print(f"docs_ownership={report.documentation_ownership_state}")
    print(f"docs_sync={report.documentation_sync_state}")
    print(f"migration={report.migration_state}")
    if report.git_readiness is not None:
        print(f"git_staged_count={len(report.git_readiness.staged_paths)}")
        print(f"git_unstaged_count={len(report.git_readiness.unstaged_paths)}")
        print(f"git_untracked_count={len(report.git_readiness.untracked_paths)}")
    print(f"issue_count={len(report.issues)}")
    for issue in report.issues:
        print(
            f"issue={issue.code}:{issue.state}:"
            f"{_single_line(issue.detail)}"
        )
    print(f"next_action={report.next_action}")


def _project_health(args: argparse.Namespace) -> int:
    report = audit_project_health(Path(args.project).resolve())
    _print_health_report(report)
    return 0 if report.overall_state == "healthy" else 1


def _project_reconcile(args: argparse.Namespace) -> int:
    if args.reconcile_action != "plan":
        raise ValueError("Unsupported reconciliation action")
    return run_reconciliation_plan(Path(args.project).resolve())


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


def _ownership_plan(project_root: Path):
    snapshot = inspect_project_state(ProjectInspectionRequest(project_root))
    return plan_documentation_ownership_initialization(snapshot)


def _ownership_status(plan) -> str:
    if plan.manual_review:
        return "manual_review"
    if plan.updates:
        return "ready"
    return "initialized"


def _ownership_check(project_root: Path) -> int:
    plan = _ownership_plan(project_root)
    status = _ownership_status(plan)

    print(f"project={plan.project_root}")
    print(f"classification_count={len(plan.classifications)}")
    print(f"initialization_count={len(plan.updates)}")
    print(f"manual_review_count={len(plan.manual_review)}")
    for item in plan.classifications:
        print(f"ownership={item.document}:{item.state}")
    print(f"status={status}")
    return 0 if status == "initialized" else 1


def _ownership_plan_command(project_root: Path) -> int:
    plan = _ownership_plan(project_root)
    status = _ownership_status(plan)

    print(f"project={plan.project_root}")
    print(f"update_count={len(plan.updates)}")
    print(f"manual_review_count={len(plan.manual_review)}")
    for update in plan.updates:
        print(f"update={update.document}:{update.original_sha256}")
    for document in plan.manual_review:
        print(f"manual_review={document}")
    print(f"status={status}")
    return 1 if plan.manual_review else 0


def _ownership_apply(project_root: Path) -> int:
    plan = _ownership_plan(project_root)
    result = apply_documentation_ownership_initialization(plan)

    print(f"project={result.project_root}")
    print(f"changed_count={len(result.changed_documents)}")
    for document in result.changed_documents:
        print(f"changed_document={document}")
    print("verification=passed")
    return 0


def _project_docs(args: argparse.Namespace) -> int:
    project_root = Path(args.project).resolve()
    if args.docs_action == "ownership":
        if args.ownership_action == "check":
            return _ownership_check(project_root)
        if args.ownership_action == "plan":
            return _ownership_plan_command(project_root)
        return _ownership_apply(project_root)
    if args.docs_action == "check":
        return _docs_check(project_root)
    if args.docs_action == "plan":
        return _docs_plan(project_root)
    return _docs_apply(project_root)


def _migration_plan(args: argparse.Namespace) -> ProjectMigrationPlan:
    return plan_project_migration(
        ProjectMigrationRequest(
            Path(args.project).resolve(),
            args.migration,
        ),
        DEFAULT_MIGRATION_REGISTRY,
    )


def _migration_status(plan: ProjectMigrationPlan) -> str:
    if plan.manual_review:
        return "manual_review"
    if plan.operations:
        return "ready"
    return "already_target"


def _print_migration_plan(plan: ProjectMigrationPlan) -> None:
    print(f"project={plan.project_root}")
    print(f"migration={plan.migration_id}")
    print(f"source_baseline={plan.source_baseline}")
    print(f"target_baseline={plan.target_baseline}")
    print(f"observation_count={len(plan.observations)}")
    print(f"operation_count={len(plan.operations)}")
    print(f"manual_review_count={len(plan.manual_review)}")
    for observation in plan.observations:
        digest = observation.original_sha256 or "none"
        print(
            f"observation={observation.path}:{observation.ownership}:"
            f"{observation.state}:{digest}"
        )
    for operation in plan.operations:
        digest = operation.original_sha256 or "none"
        print(
            f"operation={operation.path}:{operation.action}:"
            f"{operation.ownership}:{digest}"
        )
    for path in plan.manual_review:
        print(f"manual_review={path}")
    print(f"status={_migration_status(plan)}")


def _project_migrate(args: argparse.Namespace) -> int:
    plan = _migration_plan(args)
    if args.migrate_action == "check":
        _print_migration_plan(plan)
        return 1 if plan.operations or plan.manual_review else 0
    if args.migrate_action == "plan":
        _print_migration_plan(plan)
        return 1 if plan.manual_review else 0

    result = apply_project_migration(plan)
    print(f"project={result.project_root}")
    print(f"migration={result.migration_id}")
    print(f"target_baseline={result.target_baseline}")
    print(f"changed_count={len(result.changed_paths)}")
    for path in result.changed_paths:
        print(f"changed_path={path}")
    print("verification=passed")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.action == "bootstrap":
            return _bootstrap_project(args)
        if args.action == "health":
            return _project_health(args)
        if args.action == "reconcile":
            return _project_reconcile(args)
        if args.action == "docs":
            return _project_docs(args)
        if args.action == "migrate":
            return _project_migrate(args)
        return _create_project(args)
    except (
        DocumentationOwnershipError,
        DocumentationSyncError,
        EngineeringBootstrapError,
        ProjectInspectionError,
        ProjectMigrationApplyError,
        ProjectMigrationError,
        ProjectTemplateError,
        subprocess.CalledProcessError,
        OSError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except Exception:
        print("error: unexpected internal failure", file=sys.stderr)
        return 3
