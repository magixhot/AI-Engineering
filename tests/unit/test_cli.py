from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import ai_engineering.cli as cli
from ai_engineering.cli import main


def _create_arguments(target: Path, name: str = "CLI Project") -> list[str]:
    return [
        "project",
        "create",
        "--name",
        name,
        "--destination",
        str(target),
        "--description",
        "CLI test project.",
    ]


def _bootstrap_arguments(target: Path, name: str = "Bootstrap Project") -> list[str]:
    return [
        "project",
        "bootstrap",
        "--name",
        name,
        "--destination",
        str(target),
        "--description",
        "Bootstrap CLI test project.",
    ]


def test_cli_help_and_missing_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match="0"):
        main(["--help"])
    assert "ai-engineering" in capsys.readouterr().out

    with pytest.raises(SystemExit, match="2"):
        main(["project", "create"])
    assert "required" in capsys.readouterr().err


def test_cli_project_help_lists_create_and_bootstrap(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit, match="0"):
        main(["project", "--help"])

    output = capsys.readouterr().out
    assert "create" in output
    assert "bootstrap" in output


def test_cli_creates_v1_project_and_reports_success(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main(_create_arguments(tmp_path / "project"))

    assert result == 0
    assert capsys.readouterr().out.splitlines() == [
        "project_name=CLI Project",
        f"created_project={(tmp_path / 'project').resolve()}",
        f"project_path={(tmp_path / 'project').resolve()}",
        "git_branch=main",
        "initial_commit=created",
    ]


def test_cli_scaffold_and_expected_error_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = tmp_path / "scaffold"
    result = main(
        ["project", "create", "--name", "CLI Scaffold", "--destination",
         str(target), "--description", "CLI scaffold.", "--python-scaffold"]
    )
    assert result == 0
    assert "package_name=cli_scaffold" in capsys.readouterr().out

    assert main(
        ["project", "create", "--name", "Again", "--destination", str(target),
         "--description", "Existing."]
    ) == 1
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert "Traceback" not in captured.err


def test_cli_preserves_nested_git_protection(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    assert main(_create_arguments(tmp_path / "nested")) == 1
    assert "inside an existing Git repository" in capsys.readouterr().err


def test_cli_rejects_invalid_scaffold_package_name(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    arguments = _create_arguments(tmp_path / "invalid", name="!!!")
    arguments.append("--python-scaffold")

    assert main(arguments) == 1
    assert "Invalid package name" in capsys.readouterr().err


def test_cli_initial_commit_contains_generated_files(tmp_path: Path) -> None:
    target = tmp_path / "commit"

    assert main(_create_arguments(target)) == 0

    committed_files = subprocess.run(
        ["git", "ls-tree", "--name-only", "-r", "HEAD"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    assert "README.md" in committed_files
    assert "pyproject.toml" not in committed_files


def test_cli_unexpected_failure_uses_exit_code_three(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_unexpectedly(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("unexpected")

    monkeypatch.setattr(cli, "create_standalone_project", fail_unexpectedly)

    assert main(_create_arguments(tmp_path / "unexpected")) == 3
    captured = capsys.readouterr()
    assert captured.err == "error: unexpected internal failure\n"


def test_bootstrap_cli_creates_verified_project_and_reports_success(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = tmp_path / "bootstrap"

    assert main(_bootstrap_arguments(target)) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.splitlines() == [
        f"bootstrapped_project={target.resolve()}",
        "project_name=Bootstrap Project",
        "profile=python-engineering",
        "package_name=bootstrap_project",
        "git_branch=main",
        "initial_commit=created",
        "verification=passed",
    ]
    assert (target / "pyproject.toml").is_file()
    assert (target / "src" / "bootstrap_project" / "__init__.py").is_file()
    assert (target / "tests" / "test_smoke.py").is_file()


def test_bootstrap_cli_rejects_unknown_profile_without_success_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    arguments = _bootstrap_arguments(tmp_path / "invalid-profile")
    arguments.extend(["--profile", "unknown"])

    assert main(arguments) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Unsupported engineering bootstrap profile" in captured.err


def test_bootstrap_cli_preserves_nested_git_protection(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    assert main(_bootstrap_arguments(tmp_path / "nested-bootstrap")) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "inside an existing Git repository" in captured.err


def test_bootstrap_cli_unexpected_failure_uses_exit_code_three(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_unexpectedly(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("unexpected")

    monkeypatch.setattr(cli, "bootstrap_engineering_project", fail_unexpectedly)

    assert main(_bootstrap_arguments(tmp_path / "unexpected-bootstrap")) == 3
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "error: unexpected internal failure\n"
