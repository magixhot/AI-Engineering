from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_reconciliation_orchestration import (
    MAX_MAX_STEPS,
    run_project_reconciliation,
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


def _bootstrap_v1(tmp_path: Path) -> Path:
    root = tmp_path / "legacy-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=root,
            project_name="Legacy Project",
            project_description="AUTO-0009 legacy fixture.",
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
            project_description="AUTO-0009 V2 fixture.",
            author="Example Maintainer",
        )
    )
    _commit_baseline(root)
    return root


def test_orchestrator_completes_multiple_steps_with_fresh_plans(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)

    result = run_project_reconciliation(root)

    assert result.state == "complete"
    assert result.successful_steps >= 2
    assert len(result.attempts) == result.successful_steps
    assert all(attempt.state == "applied" for attempt in result.attempts)
    assert all(attempt.sequence == 1 for attempt in result.attempts)
    assert result.final_plan.state == "clean"
    assert (root / ".ai-engineering.toml").is_file()


def test_orchestrator_reports_no_change_for_healthy_project(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)
    first = run_project_reconciliation(root)
    assert first.state == "complete"

    result = run_project_reconciliation(root)

    assert result.state == "no_change"
    assert result.successful_steps == 0
    assert result.attempts == ()
    assert result.final_plan.state == "clean"


def test_orchestrator_stops_at_progress_limit(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)

    result = run_project_reconciliation(root, max_steps=1)

    assert result.state == "limit_reached"
    assert result.successful_steps == 1
    assert len(result.attempts) == 1
    assert result.attempts[0].state == "applied"
    assert result.final_plan.state == "ready"
    assert result.issues[0].code == "PROGRESS_LIMIT_REACHED"


def test_orchestrator_rejects_invalid_progress_limits(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)

    with pytest.raises(ValueError, match="at least 1"):
        run_project_reconciliation(root, max_steps=0)
    with pytest.raises(ValueError, match="must not exceed"):
        run_project_reconciliation(root, max_steps=MAX_MAX_STEPS + 1)


def test_orchestrator_stops_unsupported_project_without_writes(tmp_path: Path) -> None:
    root = tmp_path / "unsupported"
    root.mkdir()
    before = tuple(root.iterdir())

    result = run_project_reconciliation(root)

    assert result.state == "stopped"
    assert result.successful_steps == 0
    assert result.attempts == ()
    assert result.final_plan.state == "unsupported"
    assert result.issues[0].code == "PLAN_UNSUPPORTED"
    assert tuple(root.iterdir()) == before
