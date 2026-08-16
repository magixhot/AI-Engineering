from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering.cli import main
from ai_engineering.documentation_ownership import (
    apply_documentation_ownership_initialization,
    plan_documentation_ownership_initialization,
)
from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_inspection import (
    ProjectInspectionRequest,
    inspect_project_state,
)
from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)


def _bootstrap_v1(tmp_path: Path) -> Path:
    target = tmp_path / "legacy-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=target,
            project_name="Legacy Project",
            project_description="AUTO-0007 CLI fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    return target


def _bootstrap_v2(tmp_path: Path) -> Path:
    target = tmp_path / "v2-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=target,
            project_name="V2 Project",
            project_description="AUTO-0007 CLI fixture.",
            author="Example Maintainer",
        )
    )
    return target


def _initialize_ownership(root: Path) -> None:
    snapshot = inspect_project_state(ProjectInspectionRequest(root))
    plan = plan_documentation_ownership_initialization(snapshot)
    assert not plan.manual_review
    assert plan.updates
    apply_documentation_ownership_initialization(plan)


def _arguments(root: Path) -> list[str]:
    return [
        "project",
        "reconcile",
        "plan",
        "--project",
        str(root),
    ]


def test_cli_project_help_lists_reconcile(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit, match="0"):
        main(["project", "--help"])

    assert "reconcile" in capsys.readouterr().out


def test_cli_reconcile_help_lists_plan(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit, match="0"):
        main(["project", "reconcile", "--help"])

    assert "plan" in capsys.readouterr().out


def test_cli_reconcile_v1_is_deterministic_and_read_only(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _bootstrap_v1(tmp_path)
    before = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }

    assert main(_arguments(root)) == 0
    first = capsys.readouterr().out

    assert "state=ready" in first
    assert "current_overall=action_required" in first
    assert "step_count=1" in first
    assert "step=1:project migrate plan --migration python-engineering-v1-to-v2:ready:" in first
    assert "step_migration=1:python-engineering-v1-to-v2" in first
    assert "step_reinspect=1:true" in first
    assert "reinspect_required=true" in first
    assert "issue_count=0" in first
    assert "expected_state=reinspect_required" in first

    assert main(_arguments(root)) == 0
    assert capsys.readouterr().out == first
    assert {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    } == before


def test_cli_reconcile_healthy_v2_returns_clean(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _bootstrap_v2(tmp_path)
    _initialize_ownership(root)

    assert main(_arguments(root)) == 0
    assert capsys.readouterr().out.splitlines() == [
        f"project={root.resolve()}",
        "state=clean",
        "current_overall=healthy",
        "step_count=0",
        "reinspect_required=false",
        "issue_count=0",
        "expected_state=healthy",
    ]


def test_cli_reconcile_unsupported_returns_controlled_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _bootstrap_v1(tmp_path)
    (root / ".ai-engineering.toml").write_text(
        'profile = "python-engineering"\nbaseline = "unapproved"\n',
        encoding="utf-8",
    )

    assert main(_arguments(root)) == 1
    output = capsys.readouterr().out
    assert "state=unsupported" in output
    assert "current_overall=unsupported" in output
    assert "step_count=0" in output
    assert "reinspect_required=false" in output
    assert "issue_count=1" in output
    assert "issue=IDENTITY_UNSUPPORTED:unsupported:" in output
    assert "expected_state=unsupported" in output
