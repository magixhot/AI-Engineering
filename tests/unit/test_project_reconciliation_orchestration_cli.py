from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import cast

import ai_engineering.public_cli as public_cli
from ai_engineering.project_reconciliation import ProjectReconciliationPlan
from ai_engineering.project_reconciliation_orchestration import (
    ProjectReconciliationOrchestrationIssue,
    ProjectReconciliationOrchestrationResult,
)
from ai_engineering.project_reconciliation_orchestration_cli import (
    print_reconciliation_run_result,
)


def _plan() -> ProjectReconciliationPlan:
    return cast(
        ProjectReconciliationPlan,
        SimpleNamespace(state="clean", steps=()),
    )


def test_public_cli_routes_run_with_default_limit(monkeypatch, tmp_path: Path) -> None:
    captured: list[tuple[Path, int, Path | None]] = []

    def fake_run(
        project_root: Path,
        *,
        max_steps: int,
        policy_path: Path | None,
    ) -> int:
        captured.append((project_root, max_steps, policy_path))
        return 0

    monkeypatch.setattr(public_cli, "run_reconciliation_orchestration", fake_run)

    assert public_cli.main(
        ["project", "reconcile", "run", "--project", str(tmp_path)]
    ) == 0
    assert captured == [(tmp_path.resolve(), 8, None)]


def test_public_cli_routes_run_with_bounded_limit_and_policy(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: list[tuple[int, Path | None]] = []
    policy = tmp_path / "policy.toml"

    def fake_run(
        project_root: Path,
        *,
        max_steps: int,
        policy_path: Path | None,
    ) -> int:
        captured.append((max_steps, policy_path))
        return 1

    monkeypatch.setattr(public_cli, "run_reconciliation_orchestration", fake_run)

    assert public_cli.main(
        [
            "project",
            "reconcile",
            "run",
            "--project",
            str(tmp_path),
            "--max-steps",
            "3",
            "--policy",
            str(policy),
        ]
    ) == 1
    assert captured == [(3, policy.resolve())]


def test_public_cli_rejects_unbounded_or_invalid_limits(tmp_path: Path) -> None:
    for value in ("0", "101"):
        assert public_cli.main(
            [
                "project",
                "reconcile",
                "run",
                "--project",
                str(tmp_path),
                "--max-steps",
                value,
            ]
        ) == 2


def test_public_cli_preserves_existing_commands(monkeypatch) -> None:
    captured: list[list[str]] = []

    def fake_legacy(argv) -> int:
        captured.append(list(argv))
        return 7

    monkeypatch.setattr(public_cli, "legacy_main", fake_legacy)
    argv = ["project", "reconcile", "plan", "--project", "."]

    assert public_cli.main(argv) == 7
    assert captured == [argv]


def test_run_result_prints_deterministic_terminal_evidence(
    capsys,
    tmp_path: Path,
) -> None:
    result = ProjectReconciliationOrchestrationResult(
        project_root=tmp_path.resolve(),
        state="stopped",
        successful_steps=0,
        attempts=(),
        policy_decisions=(),
        final_plan=_plan(),
        issues=(
            ProjectReconciliationOrchestrationIssue(
                code="PLAN_MANUAL_REVIEW",
                detail="manual\nreview required",
            ),
        ),
    )

    print_reconciliation_run_result(result)

    assert capsys.readouterr().out.splitlines() == [
        f"project={tmp_path.resolve()}",
        "state=stopped",
        "successful_steps=0",
        "attempt_count=0",
        "policy_decision_count=0",
        "issue_count=1",
        "issue=PLAN_MANUAL_REVIEW:manual review required",
        "final_plan_state=clean",
        "remaining_step_count=0",
    ]
