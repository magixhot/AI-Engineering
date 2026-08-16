"""Public console entry point with AUTO-0009 orchestration routing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .cli import main as legacy_main
from .project_reconciliation_orchestration import DEFAULT_MAX_STEPS, MAX_MAX_STEPS
from .project_reconciliation_orchestration_cli import run_reconciliation_orchestration


def _run_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-engineering project reconcile run")
    parser.add_argument("--project", required=True)
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS)
    return parser


def _is_reconciliation_run(argv: Sequence[str]) -> bool:
    return len(argv) >= 3 and list(argv[:3]) == ["project", "reconcile", "run"]


def main(argv: Sequence[str] | None = None) -> int:
    """Route AUTO-0009 run while preserving all existing CLI commands."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if not _is_reconciliation_run(arguments):
        return legacy_main(arguments)

    args = _run_parser().parse_args(arguments[3:])
    if args.max_steps < 1 or args.max_steps > MAX_MAX_STEPS:
        print(
            f"error: --max-steps must be between 1 and {MAX_MAX_STEPS}",
            file=sys.stderr,
        )
        return 2
    return run_reconciliation_orchestration(
        Path(args.project).resolve(),
        max_steps=args.max_steps,
    )
