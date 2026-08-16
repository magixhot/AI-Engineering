from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import ai_engineering.project_reconciliation_orchestration as orchestration
from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_reconciliation_apply import (
    ProjectReconciliationApplyIssue,
    ProjectReconciliationApplyResult,
)
from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
        shell=False,
        stdin=subprocess.DEVNULL,
    ).stdout.rstrip("\r\n")


def _commit_baseline(root: Path) -> None:
    _git(root, "config", "user.name", "Test User")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "add", "-A")
    _git(root, "commit", "--allow-empty", "-m", "baseline")


def _bootstrap_v1(tmp_path: Path, name: str = "legacy-project") -> Path:
    root = tmp_path / name
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=root,
            project_name="Legacy Project",
            project_description="AUTO-0009 invariant fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    _commit_baseline(root)
    return root


def _bootstrap_v2(tmp_path: Path) -> Path:
    root = tmp_path / "v2-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=root,
            project_name="V2 Project",
            project_description="AUTO-0009 invariant fixture.",
            author="Example Maintainer",
        )
    )
    _commit_baseline(root)
    return root


def _git_invariants(root: Path) -> tuple[str, str, str, str, str]:
    return (
        _git(root, "rev-parse", "HEAD"),
        _git(root, "branch", "--show-current"),
        _git(root, "diff", "--cached", "--binary"),
        _git(root, "remote", "-v"),
        _git(root, "config", "--local", "--list"),
    )


def _refusal_result(
    root: Path,
    *,
    workflow: str,
    state: str,
    code: str,
) -> ProjectReconciliationApplyResult:
    return ProjectReconciliationApplyResult(
        project_root=root.resolve(),
        sequence=1,
        workflow=workflow,
        state=state,  # type: ignore[arg-type]
        write_attempted=False,
        delegated_subsystem=None,
        issues=(ProjectReconciliationApplyIssue(code=code, detail=code.lower()),),
        rollback_status="not_applicable",
        reinspect_required=False,
        post_apply_state="unknown",
    )


def test_orchestrator_replans_after_every_successful_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _bootstrap_v1(tmp_path)
    real_plan = orchestration.plan_project_reconciliation
    plan_states: list[str] = []

    def counting_plan(project_root: Path):  # type: ignore[no-untyped-def]
        plan = real_plan(project_root)
        plan_states.append(plan.state)
        return plan

    monkeypatch.setattr(orchestration, "plan_project_reconciliation", counting_plan)

    result = orchestration.run_project_reconciliation(root)

    assert result.state == "complete"
    assert result.successful_steps >= 2
    assert len(plan_states) == len(result.attempts) + 1
    assert plan_states[-1] == "clean"
    assert all(attempt.sequence == 1 for attempt in result.attempts)


def test_orchestrator_preserves_git_invariants_across_multi_step_success(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v1(tmp_path)
    before = _git_invariants(root)

    result = orchestration.run_project_reconciliation(root)

    assert result.state == "complete"
    assert result.successful_steps >= 2
    assert _git_invariants(root) == before


def test_orchestrator_stops_on_stale_delegate_without_retrying(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _bootstrap_v2(tmp_path)
    initial = orchestration.plan_project_reconciliation(root)
    assert initial.state == "ready"
    workflow = initial.steps[0].workflow
    calls = 0

    def stale_once(plan, sequence):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        assert sequence == 1
        return _refusal_result(
            root,
            workflow=plan.steps[0].workflow,
            state="stale_plan",
            code="STALE_PLAN",
        )

    monkeypatch.setattr(orchestration, "apply_project_reconciliation_step", stale_once)
    before = tuple(path.read_bytes() for path in sorted(root.glob("*.md")))

    result = orchestration.run_project_reconciliation(root)

    assert result.state == "stopped"
    assert result.successful_steps == 0
    assert len(result.attempts) == 1
    assert result.attempts[0].state == "stale_plan"
    assert result.issues[0].code == "DELEGATED_STEP_REFUSED"
    assert calls == 1
    assert workflow == result.attempts[0].workflow
    assert tuple(path.read_bytes() for path in sorted(root.glob("*.md"))) == before


def test_orchestrator_reports_partial_progress_without_global_rollback_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _bootstrap_v1(tmp_path)
    real_apply = orchestration.apply_project_reconciliation_step
    calls = 0

    def fail_second(plan, sequence):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        if calls == 1:
            return real_apply(plan, sequence)
        return ProjectReconciliationApplyResult(
            project_root=root.resolve(),
            sequence=sequence,
            workflow=plan.steps[0].workflow,
            state="failed",
            write_attempted=True,
            delegated_subsystem="AUTO-0003",
            issues=(
                ProjectReconciliationApplyIssue(
                    code="DELEGATED_APPLY_FAILED",
                    detail="synthetic later-step failure",
                ),
            ),
            rollback_status="unknown",
            reinspect_required=True,
            post_apply_state="unknown",
        )

    monkeypatch.setattr(orchestration, "apply_project_reconciliation_step", fail_second)

    result = orchestration.run_project_reconciliation(root)

    assert result.state == "failed"
    assert result.successful_steps == 1
    assert len(result.attempts) == 2
    assert result.attempts[0].state == "applied"
    assert result.attempts[1].state == "failed"
    assert result.attempts[1].rollback_status == "unknown"
    assert result.issues[0].code == "DELEGATED_STEP_FAILED"
    assert (root / ".ai-engineering.toml").is_file()


def test_orchestrator_is_deterministic_for_equivalent_initial_states(
    tmp_path: Path,
) -> None:
    first_root = _bootstrap_v1(tmp_path, "first")
    second_root = _bootstrap_v1(tmp_path, "second")

    first = orchestration.run_project_reconciliation(first_root)
    second = orchestration.run_project_reconciliation(second_root)

    first_trace = tuple(
        (
            attempt.state,
            attempt.workflow,
            attempt.delegated_subsystem,
            attempt.rollback_status,
            attempt.post_apply_state,
        )
        for attempt in first.attempts
    )
    second_trace = tuple(
        (
            attempt.state,
            attempt.workflow,
            attempt.delegated_subsystem,
            attempt.rollback_status,
            attempt.post_apply_state,
        )
        for attempt in second.attempts
    )

    assert first.state == second.state == "complete"
    assert first.successful_steps == second.successful_steps
    assert first_trace == second_trace
