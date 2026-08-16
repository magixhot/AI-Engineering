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
            "GIT_AUTHOR_NAME": "AI-Engineering Health Release Tests",
            "GIT_AUTHOR_EMAIL": "health-release@example.invalid",
            "GIT_COMMITTER_NAME": "AI-Engineering Health Release Tests",
            "GIT_COMMITTER_EMAIL": "health-release@example.invalid",
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


def _health(
    cli: Path,
    project: Path,
    *,
    cwd: Path,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return _run(
        [str(cli), "project", "health", "--project", str(project)],
        cwd=cwd,
        environment=environment,
        check=False,
    )


def _git_snapshot(
    project: Path,
    environment: dict[str, str],
) -> tuple[str, str, str, str]:
    head = _run(
        ["git", "rev-parse", "HEAD"],
        cwd=project,
        environment=environment,
    ).stdout
    branch = _run(
        ["git", "branch", "--show-current"],
        cwd=project,
        environment=environment,
    ).stdout
    index = _run(
        ["git", "diff", "--cached", "--name-status"],
        cwd=project,
        environment=environment,
    ).stdout
    status = _run(
        ["git", "status", "--short"],
        cwd=project,
        environment=environment,
    ).stdout
    return head, branch, index, status


def test_installed_wheel_runs_project_health_end_to_end(tmp_path: Path) -> None:
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

    health_help = _run(
        [str(cli), "project", "health", "--help"],
        cwd=isolated,
        environment=environment,
    )
    assert "--project" in health_help.stdout

    legacy = tmp_path / "legacy-health-project"
    _run(
        [
            str(cli),
            "project",
            "create",
            "--name",
            "Legacy Health Project",
            "--destination",
            str(legacy),
            "--description",
            "Installed health V1 fixture.",
            "--python-scaffold",
        ],
        cwd=isolated,
        environment=environment,
    )
    legacy_health = _health(
        cli,
        legacy,
        cwd=isolated,
        environment=environment,
    )
    assert legacy_health.returncode == 1
    assert "overall=action_required" in legacy_health.stdout
    assert "identity=python-engineering" in legacy_health.stdout
    assert "baseline=python-engineering-v1" in legacy_health.stdout
    assert "migration=ready" in legacy_health.stdout
    expected_next_action = (
        "next_action=project migrate plan --migration "
        "python-engineering-v1-to-v2"
    )
    assert expected_next_action in legacy_health.stdout
    assert legacy_health.stderr == ""
    assert "Traceback" not in legacy_health.stdout

    healthy = tmp_path / "healthy-v2-project"
    _run(
        [
            str(cli),
            "project",
            "bootstrap",
            "--name",
            "Healthy V2 Project",
            "--destination",
            str(healthy),
            "--description",
            "Installed health V2 fixture.",
        ],
        cwd=isolated,
        environment=environment,
    )
    _run(
        [
            str(cli),
            "project",
            "docs",
            "ownership",
            "apply",
            "--project",
            str(healthy),
        ],
        cwd=isolated,
        environment=environment,
    )
    _run(
        ["git", "remote", "add", "origin", "https://example.invalid/health.git"],
        cwd=healthy,
        environment=environment,
    )
    remotes_before = _run(
        ["git", "remote", "-v"],
        cwd=healthy,
        environment=environment,
    ).stdout
    git_before = _git_snapshot(healthy, environment)

    healthy_result = _health(
        cli,
        healthy,
        cwd=isolated,
        environment=environment,
    )
    assert healthy_result.returncode == 0
    assert "overall=healthy" in healthy_result.stdout
    assert "identity=python-engineering" in healthy_result.stdout
    assert "baseline=python-engineering-v2" in healthy_result.stdout
    assert "docs_ownership=initialized" in healthy_result.stdout
    assert "docs_sync=clean" in healthy_result.stdout
    assert "migration=already_target" in healthy_result.stdout
    assert "issue_count=0" in healthy_result.stdout
    assert "next_action=none" in healthy_result.stdout
    assert healthy_result.stderr == ""
    assert _git_snapshot(healthy, environment) == git_before
    assert _run(
        ["git", "remote", "-v"],
        cwd=healthy,
        environment=environment,
    ).stdout == remotes_before

    unsupported = tmp_path / "unsupported-health-project"
    unsupported.mkdir()
    (unsupported / "pyproject.toml").write_text(
        '[project]\nname = "unsupported"\nversion = "1.0.0"\n',
        encoding="utf-8",
    )
    unsupported_result = _health(
        cli,
        unsupported,
        cwd=isolated,
        environment=environment,
    )
    assert unsupported_result.returncode == 1
    assert "overall=unsupported" in unsupported_result.stdout
    assert "identity=unsupported" in unsupported_result.stdout
    assert "baseline=unknown" in unsupported_result.stdout
    assert "next_action=manual_review" in unsupported_result.stdout
    assert unsupported_result.stderr == ""
    assert "Traceback" not in unsupported_result.stdout
