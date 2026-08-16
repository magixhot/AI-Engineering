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
            "GIT_AUTHOR_NAME": "AI-Engineering Migration Release Tests",
            "GIT_AUTHOR_EMAIL": "migration-release@example.invalid",
            "GIT_COMMITTER_NAME": "AI-Engineering Migration Release Tests",
            "GIT_COMMITTER_EMAIL": "migration-release@example.invalid",
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


def test_installed_wheel_migration_cli_is_present_and_fails_closed(
    tmp_path: Path,
) -> None:
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

    migration_help = _run(
        [str(cli), "project", "migrate", "--help"],
        cwd=isolated,
        environment=environment,
    )
    assert "check" in migration_help.stdout
    assert "plan" in migration_help.stdout
    assert "apply" in migration_help.stdout

    project = tmp_path / "installed-migration-project"
    _run(
        [
            str(cli),
            "project",
            "create",
            "--name",
            "Installed Migration Project",
            "--destination",
            str(project),
            "--description",
            "Installed wheel migration CLI verification.",
            "--python-scaffold",
        ],
        cwd=isolated,
        environment=environment,
    )
    head_before = _run(
        ["git", "rev-parse", "HEAD"],
        cwd=project,
        environment=environment,
    ).stdout.strip()

    unsupported = _run(
        [
            str(cli),
            "project",
            "migrate",
            "plan",
            "--project",
            str(project),
            "--migration",
            "unregistered",
        ],
        cwd=isolated,
        environment=environment,
        check=False,
    )
    assert unsupported.returncode == 1
    assert unsupported.stdout == ""
    assert "Unsupported migration id" in unsupported.stderr
    assert "Traceback" not in unsupported.stderr

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
