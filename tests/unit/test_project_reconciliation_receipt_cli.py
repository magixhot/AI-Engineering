from __future__ import annotations

from pathlib import Path
from typing import cast

import ai_engineering.project_reconciliation_receipt_cli as receipt_cli
import ai_engineering.public_cli as public_cli
from ai_engineering.project_reconciliation import ProjectReconciliationPlan
from ai_engineering.project_reconciliation_orchestration import (
    ProjectReconciliationOrchestrationResult,
)
from ai_engineering.project_reconciliation_receipt import ReconciliationExecutionReceipt
from ai_engineering.project_reconciliation_receipt_projection import (
    ReconciliationReceiptProjectionContext,
)


def test_public_cli_routes_explicit_receipt_json_mode(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: list[tuple[Path, int, Path | None, Path | None]] = []

    def fake_run(
        project_root: Path,
        *,
        max_steps: int,
        policy_path: Path | None,
        approval_path: Path | None,
    ) -> int:
        captured.append((project_root, max_steps, policy_path, approval_path))
        return 1

    monkeypatch.setattr(
        public_cli,
        "run_reconciliation_orchestration_receipt",
        fake_run,
    )

    assert public_cli.main(
        [
            "project",
            "reconcile",
            "run",
            "--project",
            str(tmp_path),
            "--receipt-json",
        ]
    ) == 1
    assert captured == [(tmp_path.resolve(), 8, None, None)]


def test_receipt_mode_runs_existing_orchestration_once_and_emits_only_json(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    initial_plan = cast(ProjectReconciliationPlan, object())
    result = cast(ProjectReconciliationOrchestrationResult, object())
    context = cast(ReconciliationReceiptProjectionContext, object())
    receipt = cast(ReconciliationExecutionReceipt, object())
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(
        receipt_cli,
        "plan_project_reconciliation",
        lambda root: calls.append(("plan", root)) or initial_plan,
    )

    def fake_run(
        root: Path,
        *,
        max_steps: int,
        policy_path: Path | None,
        approval_path: Path | None,
    ) -> ProjectReconciliationOrchestrationResult:
        calls.append(("run", (root, max_steps, policy_path, approval_path)))
        return result

    monkeypatch.setattr(receipt_cli, "run_project_reconciliation", fake_run)
    monkeypatch.setattr(
        receipt_cli,
        "_receipt_context",
        lambda *args, **kwargs: context,
    )
    monkeypatch.setattr(
        receipt_cli,
        "project_reconciliation_execution_receipt",
        lambda observed, observed_context: (
            calls.append(("project", (observed, observed_context))) or receipt
        ),
    )
    monkeypatch.setattr(
        receipt_cli,
        "serialize_reconciliation_execution_receipt",
        lambda value: b'{"kind":"reconciliation_execution"}\n',
    )

    # The fake result is only used by the final exit-code check.
    class _Result:
        state = "complete"

    result = cast(ProjectReconciliationOrchestrationResult, _Result())

    assert receipt_cli.run_reconciliation_orchestration_receipt(tmp_path) == 0
    assert capsys.readouterr().out == '{"kind":"reconciliation_execution"}\n'
    assert [name for name, _ in calls] == ["plan", "run", "project"]
