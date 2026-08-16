from __future__ import annotations

from pathlib import Path

import pytest

import ai_engineering.cli as cli
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
    root = tmp_path / "health-cli-v1"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=root,
            project_name="Health CLI V1",
            project_description="AUTO-0006 CLI legacy fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    return root


def _bootstrap_v2(tmp_path: Path) -> Path:
    root = tmp_path / "health-cli-v2"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=root,
            project_name="Health CLI V2",
            project_description="AUTO-0006 CLI V2 fixture.",
            author="Example Maintainer",
        )
    )
    return root


def _initialize_ownership(root: Path) -> None:
    snapshot = inspect_project_state(ProjectInspectionRequest(root))
    plan = plan_documentation_ownership_initialization(snapshot)
    assert not plan.manual_review
    apply_documentation_ownership_initialization(plan)


def test_project_help_lists_health(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match="0"):
        cli.main(["project", "--help"])

    output = capsys.readouterr().out
    assert "health" in output


def test_health_cli_reports_v1_action_required(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _bootstrap_v1(tmp_path)

    assert cli.main(["project", "health", "--project", str(root)]) == 1

    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == f"project={root.resolve()}"
    assert lines[1] == "overall=action_required"
    assert "identity=python-engineering" in lines
    assert "baseline=python-engineering-v1" in lines
    assert "git=ready_clean" in lines
    assert "migration=ready" in lines
    assert any(line.startswith("issue=MIGRATION_AVAILABLE:") for line in lines)
    assert lines[-1] == (
        "next_action=project migrate plan --migration "
        "python-engineering-v1-to-v2"
    )


def test_health_cli_reports_healthy_v2_with_exit_zero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _bootstrap_v2(tmp_path)
    _initialize_ownership(root)

    assert cli.main(["project", "health", "--project", str(root)]) == 0

    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == f"project={root.resolve()}"
    assert lines[1] == "overall=healthy"
    assert "baseline=python-engineering-v2" in lines
    assert "docs_ownership=initialized" in lines
    assert "docs_sync=clean" in lines
    assert "migration=already_target" in lines
    assert "issue_count=0" in lines
    assert lines[-1] == "next_action=none"


def test_health_cli_unsupported_is_controlled_without_traceback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "unsupported"
    root.mkdir()
    (root / "pyproject.toml").write_text(
        '[project]\nname = "unsupported"\nversion = "1.0.0"\n',
        encoding="utf-8",
    )

    assert cli.main(["project", "health", "--project", str(root)]) == 1

    captured = capsys.readouterr()
    assert "overall=unsupported" in captured.out
    assert "identity=unsupported" in captured.out
    assert "baseline=unknown" in captured.out
    assert "next_action=manual_review" in captured.out
    assert "Traceback" not in captured.out
    assert "Traceback" not in captured.err
