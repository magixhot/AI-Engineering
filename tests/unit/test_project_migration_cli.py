from __future__ import annotations

from pathlib import Path

import pytest

import ai_engineering.cli as cli
from ai_engineering.project_migration import (
    ACTION_CREATE_FILE,
    OWNERSHIP_GENERATED_ABSENT,
    PYTHON_ENGINEERING_V1_BASELINE,
    MigrationContract,
    MigrationPathRule,
    MigrationRegistry,
)
from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "migration-cli-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=root,
            project_name="Migration CLI Project",
            project_description="AUTO-0004 CLI verification fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    return root


def _registry() -> MigrationRegistry:
    return MigrationRegistry(
        (
            MigrationContract(
                migration_id="v1-add-marker",
                source_baselines=(PYTHON_ENGINEERING_V1_BASELINE,),
                target_baseline="python-engineering-v2-test",
                profiles=("python-engineering",),
                rules=(
                    MigrationPathRule(
                        path=".ai-engineering-migration-test",
                        action=ACTION_CREATE_FILE,
                        ownership=OWNERSHIP_GENERATED_ABSENT,
                        target_content=b"verified\n",
                    ),
                ),
            ),
        )
    )


def _arguments(action: str, root: Path) -> list[str]:
    return [
        "project",
        "migrate",
        action,
        "--project",
        str(root),
        "--migration",
        "v1-add-marker",
    ]


def test_migration_help_lists_check_plan_and_apply(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit, match="0"):
        cli.main(["project", "migrate", "--help"])

    output = capsys.readouterr().out
    assert "check" in output
    assert "plan" in output
    assert "apply" in output


def test_registered_migration_cli_check_plan_apply_and_idempotency(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _project(tmp_path)
    marker = root / ".ai-engineering-migration-test"
    monkeypatch.setattr(cli, "DEFAULT_MIGRATION_REGISTRY", _registry())

    assert cli.main(_arguments("check", root)) == 1
    check_output = capsys.readouterr().out.splitlines()
    assert check_output[0] == f"project={root.resolve()}"
    assert "migration=v1-add-marker" in check_output
    assert "operation_count=1" in check_output
    assert "manual_review_count=0" in check_output
    assert check_output[-1] == "status=ready"
    assert not marker.exists()

    assert cli.main(_arguments("plan", root)) == 0
    first_plan = capsys.readouterr().out
    assert "operation_count=1" in first_plan
    assert "status=ready" in first_plan
    assert not marker.exists()

    assert cli.main(_arguments("plan", root)) == 0
    assert capsys.readouterr().out == first_plan
    assert not marker.exists()

    assert cli.main(_arguments("apply", root)) == 0
    apply_output = capsys.readouterr().out.splitlines()
    assert apply_output == [
        f"project={root.resolve()}",
        "migration=v1-add-marker",
        "target_baseline=python-engineering-v2-test",
        "changed_count=1",
        "changed_path=.ai-engineering-migration-test",
        "verification=passed",
    ]
    assert marker.read_bytes() == b"verified\n"

    assert cli.main(_arguments("check", root)) == 0
    clean_output = capsys.readouterr().out
    assert "operation_count=0" in clean_output
    assert "manual_review_count=0" in clean_output
    assert "status=already_target" in clean_output


def test_default_registry_fails_closed_without_traceback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _project(tmp_path)

    assert (
        cli.main(
            [
                "project",
                "migrate",
                "plan",
                "--project",
                str(root),
                "--migration",
                "unregistered",
            ]
        )
        == 1
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Unsupported migration id" in captured.err
    assert "Traceback" not in captured.err
