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


def _docs_arguments(action: str, target: Path) -> list[str]:
    return ["project", "docs", action, "--project", str(target)]


def _managed_document(marker: str, body: str) -> str:
    return (
        "# Document\n\nHuman content\n\n"
        f"<!-- ai-engineering:auto0002:{marker}:start -->"
        f"{body}"
        f"<!-- ai-engineering:auto0002:{marker}:end -->\n"
        "\nHuman tail\n"
    )


def _docs_project(tmp_path: Path) -> Path:
    root = tmp_path / "docs-project"
    (root / "src" / "sample_pkg").mkdir(parents=True)
    (root / "src" / "sample_pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / "README.md").write_text("# Sample\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nname = "sample-project"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (root / "CURRENT_STATUS.md").write_text(
        _managed_document("current-status", "\n- stale: value\n"),
        encoding="utf-8",
    )
    (root / "PROJECT_MAP.md").write_text(
        _managed_document("project-map", "\n- `gone.txt` (file)\n"),
        encoding="utf-8",
    )
    (root / "MASTER_INDEX.md").write_text(
        _managed_document("master-index", "\n- `OLD.md` — observed\n"),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=CLI Docs Test",
            "-c",
            "user.email=cli-docs@example.invalid",
            "commit",
            "-m",
            "initial",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return root


def test_cli_help_and_missing_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match="0"):
        main(["--help"])
    assert "ai-engineering" in capsys.readouterr().out

    with pytest.raises(SystemExit, match="2"):
        main(["project", "create"])
    assert "required" in capsys.readouterr().err


def test_cli_project_help_lists_create_bootstrap_and_docs(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit, match="0"):
        main(["project", "--help"])

    output = capsys.readouterr().out
    assert "create" in output
    assert "bootstrap" in output
    assert "docs" in output


def test_cli_docs_help_lists_check_plan_and_apply(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit, match="0"):
        main(["project", "docs", "--help"])

    output = capsys.readouterr().out
    assert "check" in output
    assert "plan" in output
    assert "apply" in output


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
        [
            "project",
            "create",
            "--name",
            "CLI Scaffold",
            "--destination",
            str(target),
            "--description",
            "CLI scaffold.",
            "--python-scaffold",
        ]
    )
    assert result == 0
    assert "package_name=cli_scaffold" in capsys.readouterr().out

    assert (
        main(
            [
                "project",
                "create",
                "--name",
                "Again",
                "--destination",
                str(target),
                "--description",
                "Existing.",
            ]
        )
        == 1
    )
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


def test_docs_check_and_plan_are_read_only_and_deterministic(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _docs_project(tmp_path)
    before = {path: path.read_bytes() for path in root.glob("*.md")}

    assert main(_docs_arguments("check", root)) == 1
    check_output = capsys.readouterr().out.splitlines()
    assert check_output[0] == f"project={root.resolve()}"
    assert "manual_review_count=0" in check_output
    assert check_output[-1] == "status=drift"

    assert main(_docs_arguments("plan", root)) == 0
    first_plan = capsys.readouterr().out
    assert "update_count=3" in first_plan
    assert "manual_review_count=0" in first_plan
    assert "status=ready" in first_plan
    assert first_plan.count("update=") == 3

    assert main(_docs_arguments("plan", root)) == 0
    assert capsys.readouterr().out == first_plan
    assert {path: path.read_bytes() for path in root.glob("*.md")} == before


def test_docs_apply_updates_only_managed_docs_and_preserves_git_head(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _docs_project(tmp_path)
    readme_before = (root / "README.md").read_bytes()
    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert main(_docs_arguments("apply", root)) == 0
    apply_output = capsys.readouterr().out.splitlines()
    assert apply_output == [
        f"project={root.resolve()}",
        "changed_count=3",
        "changed_document=CURRENT_STATUS.md",
        "changed_document=MASTER_INDEX.md",
        "changed_document=PROJECT_MAP.md",
        "verification=passed",
    ]
    assert (root / "README.md").read_bytes() == readme_before

    head_after = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert head_after == head_before
    assert (
        subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        == ""
    )

    assert main(_docs_arguments("check", root)) == 0
    assert capsys.readouterr().out.splitlines() == [
        f"project={root.resolve()}",
        "drift_count=0",
        "manual_review_count=0",
        "status=clean",
    ]


def test_docs_apply_refuses_manual_review_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "bootstrap-no-markers"
    assert main(_bootstrap_arguments(root)) == 0
    capsys.readouterr()

    assert main(_docs_arguments("check", root)) == 1
    check_output = capsys.readouterr().out
    assert "manual_review_count=3" in check_output
    assert "status=drift" in check_output

    assert main(_docs_arguments("plan", root)) == 1
    plan_output = capsys.readouterr().out
    assert "update_count=0" in plan_output
    assert "manual_review_count=3" in plan_output
    assert "status=manual_review" in plan_output

    assert main(_docs_arguments("apply", root)) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Manual review required before documentation apply" in captured.err
    assert "verification=passed" not in captured.err
