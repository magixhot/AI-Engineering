from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
import venv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_VERSION = tomllib.loads(
    (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
)["project"]["version"]


def _environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment.update(
        {
            "GIT_AUTHOR_NAME": "AI-Engineering Ownership Release Tests",
            "GIT_AUTHOR_EMAIL": "ownership-release@example.invalid",
            "GIT_COMMITTER_NAME": "AI-Engineering Ownership Release Tests",
            "GIT_COMMITTER_EMAIL": "ownership-release@example.invalid",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        }
    )
    return environment


def _run(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=check,
        capture_output=True,
        text=True,
    )


def _venv_executable(venv_directory: Path, name: str) -> Path:
    scripts = venv_directory / ("Scripts" if os.name == "nt" else "bin")
    suffix = ".exe" if os.name == "nt" and name == "ai-engineering" else ""
    return scripts / f"{name}{suffix}"


def test_installed_wheel_ownership_cli_handoff(tmp_path: Path) -> None:
    environment = _environment()
    source_tree = tmp_path / "source"
    artifacts = tmp_path / "artifacts"
    isolated = tmp_path / "isolated"
    shutil.copytree(
        PROJECT_ROOT,
        source_tree,
        ignore=shutil.ignore_patterns(
            ".git",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".venv",
            "__pycache__",
            "*.egg-info",
            "build",
            "dist",
        ),
    )
    artifacts.mkdir()
    isolated.mkdir()

    _run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(artifacts)],
        cwd=source_tree,
        environment=environment,
    )
    wheel = next(artifacts.glob(f"ai_engineering-{PROJECT_VERSION}-*.whl"))

    venv_directory = tmp_path / "venv"
    venv.create(venv_directory, with_pip=True)
    python = _venv_executable(venv_directory, "python")
    cli = _venv_executable(venv_directory, "ai-engineering")
    _run(
        [str(python), "-m", "pip", "install", str(wheel)],
        cwd=isolated,
        environment=environment,
    )

    ownership_help = _run(
        [str(cli), "project", "docs", "ownership", "--help"],
        cwd=isolated,
        environment=environment,
    )
    assert "check" in ownership_help.stdout
    assert "plan" in ownership_help.stdout
    assert "apply" in ownership_help.stdout

    project = tmp_path / "installed-ownership-project"
    _run(
        [
            str(cli),
            "project",
            "bootstrap",
            "--name",
            "Installed Ownership Project",
            "--destination",
            str(project),
            "--description",
            "Installed wheel ownership initialization verification.",
        ],
        cwd=isolated,
        environment=environment,
    )
    head_before = _run(
        ["git", "rev-parse", "HEAD"],
        cwd=project,
        environment=environment,
    ).stdout.strip()

    check_before = _run(
        [
            str(cli),
            "project",
            "docs",
            "ownership",
            "check",
            "--project",
            str(project),
        ],
        cwd=isolated,
        environment=environment,
        check=False,
    )
    assert check_before.returncode == 1
    assert "initialization_count=3" in check_before.stdout
    assert "manual_review_count=0" in check_before.stdout
    assert "status=ready" in check_before.stdout

    plan = _run(
        [
            str(cli),
            "project",
            "docs",
            "ownership",
            "plan",
            "--project",
            str(project),
        ],
        cwd=isolated,
        environment=environment,
    )
    assert "update_count=3" in plan.stdout
    assert "manual_review_count=0" in plan.stdout
    assert plan.stdout.count("update=") == 3
    assert "status=ready" in plan.stdout

    applied = _run(
        [
            str(cli),
            "project",
            "docs",
            "ownership",
            "apply",
            "--project",
            str(project),
        ],
        cwd=isolated,
        environment=environment,
    )
    assert "changed_count=3" in applied.stdout
    assert applied.stdout.count("changed_document=") == 3
    assert "verification=passed" in applied.stdout

    assert _run(
        ["git", "rev-parse", "HEAD"],
        cwd=project,
        environment=environment,
    ).stdout.strip() == head_before
    assert _run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=project,
        environment=environment,
    ).stdout == ""

    ownership_clean = _run(
        [
            str(cli),
            "project",
            "docs",
            "ownership",
            "check",
            "--project",
            str(project),
        ],
        cwd=isolated,
        environment=environment,
    )
    assert "initialization_count=0" in ownership_clean.stdout
    assert "manual_review_count=0" in ownership_clean.stdout
    assert ownership_clean.stdout.count(":initialized") == 3
    assert "status=initialized" in ownership_clean.stdout

    sync_clean = _run(
        [
            str(cli),
            "project",
            "docs",
            "check",
            "--project",
            str(project),
        ],
        cwd=isolated,
        environment=environment,
    )
    assert "drift_count=0" in sync_clean.stdout
    assert "manual_review_count=0" in sync_clean.stdout
    assert "status=clean" in sync_clean.stdout
