"""Public console entry point with reconciliation and doctor routing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .cli import main as legacy_main
from .project_reconciliation import plan_project_reconciliation
from .project_reconciliation_approval import serialize_reconciliation_approval
from .project_reconciliation_approval_context import (
    ReconciliationApprovalContextError,
    build_approval_for_plan,
)
from .project_reconciliation_orchestration import DEFAULT_MAX_STEPS, MAX_MAX_STEPS
from .project_reconciliation_orchestration_cli import run_reconciliation_orchestration
from .project_reconciliation_receipt_cli import (
    run_reconciliation_orchestration_receipt,
)
from .workstation_doctor_runtime import probe_workstation, render_doctor_report


def _run_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-engineering project reconcile run")
    parser.add_argument("--project", required=True)
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS)
    parser.add_argument("--policy")
    parser.add_argument("--approval")
    parser.add_argument("--receipt-json", action="store_true")
    return parser


def _approval_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-engineering project reconcile approve")
    parser.add_argument("--project", required=True)
    parser.add_argument("--policy")
    return parser


def _doctor_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-engineering workstation doctor")
    parser.add_argument(
        "--repository-root",
        default=".",
        help="candidate repository root to validate; defaults to current directory",
    )
    return parser


def _is_reconciliation_action(argv: Sequence[str], action: str) -> bool:
    return len(argv) >= 3 and list(argv[:3]) == ["project", "reconcile", action]


def _is_doctor_action(argv: Sequence[str]) -> bool:
    return len(argv) >= 2 and list(argv[:2]) == ["workstation", "doctor"]


def _approval_command(arguments: Sequence[str]) -> int:
    args = _approval_parser().parse_args(arguments)
    root = Path(args.project).resolve()
    policy_path = Path(args.policy).resolve() if args.policy is not None else None
    plan = plan_project_reconciliation(root)
    try:
        approval = build_approval_for_plan(plan, policy_path=policy_path)
    except ReconciliationApprovalContextError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(serialize_reconciliation_approval(approval).decode("utf-8"), end="")
    return 0


def _doctor_command(arguments: Sequence[str]) -> int:
    args = _doctor_parser().parse_args(arguments)
    report = probe_workstation(Path(args.repository_root).resolve())
    print(render_doctor_report(report))
    return 0 if report.ready else 1


def main(argv: Sequence[str] | None = None) -> int:
    """Route doctor/approval/run while preserving all existing CLI commands."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if _is_doctor_action(arguments):
        return _doctor_command(arguments[2:])
    if _is_reconciliation_action(arguments, "approve"):
        return _approval_command(arguments[3:])
    if not _is_reconciliation_action(arguments, "run"):
        return legacy_main(arguments)

    args = _run_parser().parse_args(arguments[3:])
    if args.max_steps < 1 or args.max_steps > MAX_MAX_STEPS:
        print(
            f"error: --max-steps must be between 1 and {MAX_MAX_STEPS}",
            file=sys.stderr,
        )
        return 2
    policy_path = Path(args.policy).resolve() if args.policy is not None else None
    approval_path = (
        Path(args.approval).resolve() if args.approval is not None else None
    )
    runner = (
        run_reconciliation_orchestration_receipt
        if args.receipt_json
        else run_reconciliation_orchestration
    )
    return runner(
        Path(args.project).resolve(),
        max_steps=args.max_steps,
        policy_path=policy_path,
        approval_path=approval_path,
    )
