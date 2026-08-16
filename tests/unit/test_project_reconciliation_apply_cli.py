from __future__ import annotations

from pathlib import Path

import pytest

import ai_engineering.cli as cli
import ai_engineering.project_reconciliation_apply_cli as apply_cli
from ai_engineering.project_reconciliation_apply import (
    ProjectReconciliationApplyIssue,
    ProjectReconciliationApplyResult,
)


def _result(root: Path, state: str) -> ProjectReconciliationApplyResult:
    issues: tuple[ProjectReconciliationApplyIssue, ...] = ()
    if state == "stale_plan":
        issues = (
            ProjectReconciliationApplyIssue(
                code="STALE_PLAN",
                detail="project state changed\nafter planning",
            ),
        )
    return ProjectReconciliationApplyResult(
        project_root=root.resolve(),
        sequence=1,
        workflow="project docs apply",
        state=state,  # type: ignore[arg-type]
        write_attempted=state == "applied",
        delegated_subsystem="AUTO-0002" if state == "applied" else None,
        issues=issues,
        rollback_status="not_applicable",
        reinspect_required=state == "applied",
        post_apply_state="healthy" if state == "applied" else "unknown",
    )


def test_public_cli_dispatches_exact_reconciliation_apply_step(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[tuple[Path, int]] = []

    def fake_run(project_root: Path, sequence: int) -> int:
        observed.append((project_root, sequence))
        return 0

    monkeypatch.setattr(cli, "run_reconciliation_apply", fake_run)

    exit_code = cli.main(
        [
            "project",
            "reconcile",
            "apply",
            "--project",
            str(tmp_path),
            "--step",
            "7",
        ]
    )

    assert exit_code == 0
    assert observed == [(tmp_path.resolve(), 7)]


@pytest.mark.parametrize(
    ("state", "expected_exit"),
    [
        ("applied", 0),
        ("no_change", 0),
        ("stale_plan", 1),
        ("manual_review", 1),
        ("unsupported", 1),
        ("failed", 1),
    ],
)
def test_apply_runner_uses_bounded_exit_codes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    state: str,
    expected_exit: int,
) -> None:
    result = _result(tmp_path, state)
    monkeypatch.setattr(apply_cli, "plan_project_reconciliation", lambda root: object())
    monkeypatch.setattr(
        apply_cli,
        "apply_project_reconciliation_step",
        lambda plan, sequence: result,
    )

    exit_code = apply_cli.run_reconciliation_apply(tmp_path, 1)
    output = capsys.readouterr().out.splitlines()

    assert exit_code == expected_exit
    assert output[0] == f"project={tmp_path.resolve()}"
    assert "sequence=1" in output
    assert f"state={state}" in output
    assert output[-1] == f"post_apply_state={result.post_apply_state}"
    assert all("\n" not in line and "\r" not in line for line in output)


def test_apply_output_sanitizes_issue_detail(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    apply_cli.print_reconciliation_apply_result(_result(tmp_path, "stale_plan"))

    output = capsys.readouterr().out.splitlines()

    assert "issue_count=1" in output
    assert "issue=STALE_PLAN:project state changed after planning" in output
    assert "write_attempted=false" in output
    assert "delegated_subsystem=none" in output
