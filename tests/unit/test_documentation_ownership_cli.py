from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_engineering.cli import main


def _bootstrap_arguments(target: Path) -> list[str]:
    return [
        "project",
        "bootstrap",
        "--name",
        "Ownership CLI Project",
        "--destination",
        str(target),
        "--description",
        "AUTO-0003 ownership CLI test project.",
    ]


def _ownership_arguments(action: str, target: Path) -> list[str]:
    return [
        "project",
        "docs",
        "ownership",
        action,
        "--project",
        str(target),
    ]


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_ownership_help_lists_check_plan_and_apply(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit, match="0"):
        main(["project", "docs", "ownership", "--help"])

    output = capsys.readouterr().out
    assert "check" in output
    assert "plan" in output
    assert "apply" in output


def test_ownership_check_and_plan_are_read_only_and_deterministic(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "project"
    assert main(_bootstrap_arguments(root)) == 0
    capsys.readouterr()
    before = {
        name: (root / name).read_bytes()
        for name in ("CURRENT_STATUS.md", "MASTER_INDEX.md", "PROJECT_MAP.md")
    }

    assert main(_ownership_arguments("check", root)) == 1
    check_output = capsys.readouterr().out.splitlines()
    assert check_output[0] == f"project={root.resolve()}"
    assert "classification_count=3" in check_output
    assert "initialization_count=3" in check_output
    assert "manual_review_count=0" in check_output
    assert check_output.count("ownership=CURRENT_STATUS.md:missing") == 1
    assert check_output.count("ownership=MASTER_INDEX.md:missing") == 1
    assert check_output.count("ownership=PROJECT_MAP.md:missing") == 1
    assert check_output[-1] == "status=ready"

    assert main(_ownership_arguments("plan", root)) == 0
    first_plan = capsys.readouterr().out
    assert "update_count=3" in first_plan
    assert "manual_review_count=0" in first_plan
    assert first_plan.count("update=") == 3
    assert "status=ready" in first_plan

    assert main(_ownership_arguments("plan", root)) == 0
    assert capsys.readouterr().out == first_plan
    assert {
        name: (root / name).read_bytes()
        for name in ("CURRENT_STATUS.md", "MASTER_INDEX.md", "PROJECT_MAP.md")
    } == before


def test_ownership_apply_initializes_and_hands_off_to_auto0002(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "project"
    assert main(_bootstrap_arguments(root)) == 0
    capsys.readouterr()
    head_before = _git(root, "rev-parse", "HEAD")

    assert main(_ownership_arguments("apply", root)) == 0
    output = capsys.readouterr().out.splitlines()
    assert output == [
        f"project={root.resolve()}",
        "changed_count=3",
        "changed_document=CURRENT_STATUS.md",
        "changed_document=MASTER_INDEX.md",
        "changed_document=PROJECT_MAP.md",
        "verification=passed",
    ]
    assert _git(root, "rev-parse", "HEAD") == head_before
    assert _git(root, "diff", "--cached", "--name-only") == ""

    assert main(_ownership_arguments("check", root)) == 0
    check_output = capsys.readouterr().out
    assert "initialization_count=0" in check_output
    assert "manual_review_count=0" in check_output
    assert check_output.count(":initialized") == 3
    assert "status=initialized" in check_output

    assert main(["project", "docs", "check", "--project", str(root)]) == 0
    sync_output = capsys.readouterr().out
    assert "drift_count=0" in sync_output
    assert "manual_review_count=0" in sync_output
    assert "status=clean" in sync_output

    assert main(_ownership_arguments("apply", root)) == 0
    idempotent = capsys.readouterr().out.splitlines()
    assert idempotent == [
        f"project={root.resolve()}",
        "changed_count=0",
        "verification=passed",
    ]


def test_ownership_apply_refuses_manual_review_without_mutation(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "project"
    assert main(_bootstrap_arguments(root)) == 0
    capsys.readouterr()

    status_path = root / "CURRENT_STATUS.md"
    status_path.write_text(
        status_path.read_text(encoding="utf-8")
        + "\n<!-- ai-engineering:auto0002:current-status:start -->\n",
        encoding="utf-8",
    )
    before = {
        name: (root / name).read_bytes()
        for name in ("CURRENT_STATUS.md", "MASTER_INDEX.md", "PROJECT_MAP.md")
    }

    assert main(_ownership_arguments("plan", root)) == 1
    plan_output = capsys.readouterr().out
    assert "manual_review_count=1" in plan_output
    assert "manual_review=CURRENT_STATUS.md" in plan_output
    assert "status=manual_review" in plan_output

    assert main(_ownership_arguments("apply", root)) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "requires manual review before apply" in captured.err
    assert {
        name: (root / name).read_bytes()
        for name in ("CURRENT_STATUS.md", "MASTER_INDEX.md", "PROJECT_MAP.md")
    } == before
