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
MIGRATION_ID = "python-engineering-v1-to-v2"
V2_MARKER = (
    "schema = 1\n"
    'profile = "python-engineering"\n'
    'baseline = "python-engineering-v2"\n'
)


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


def _migration_command(
    cli: Path,
    action: str,
    project: Path,
) -> list[str]:
    return [
        str(cli),
        "project",
        "migrate",
        action,
        "--project",
        str(project),
        "--migration",
        MIGRATION_ID,
    ]


def test_installed_wheel_runs_production_v1_to_v2_migration(
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

    check_before = _run(
        _migration_command(cli, "check", project),
        cwd=isolated,
        environment=environment,
        check=False,
    )
    assert check_before.returncode == 1
    assert "source_baseline=python-engineering-v1" in check_before.stdout
    assert "target_baseline=python-engineering-v2" in check_before.stdout
    assert "operation_count=2" in check_before.stdout
    assert "manual_review_count=0" in check_before.stdout
    assert "status=ready" in check_before.stdout

    plan_before = _run(
        _migration_command(cli, "plan", project),
        cwd=isolated,
        environment=environment,
    )
    assert "operation=.ai-engineering.toml:create_file:generated_absent:none" in (
        plan_before.stdout
    )
    assert "operation=.gitignore:replace_machine_owned_file:machine_owned:" in (
        plan_before.stdout
    )
    assert "status=ready" in plan_before.stdout

    apply_result = _run(
        _migration_command(cli, "apply", project),
        cwd=isolated,
        environment=environment,
    )
    assert f"migration={MIGRATION_ID}" in apply_result.stdout
    assert "target_baseline=python-engineering-v2" in apply_result.stdout
    assert "changed_count=2" in apply_result.stdout
    assert "changed_path=.ai-engineering.toml" in apply_result.stdout
    assert "changed_path=.gitignore" in apply_result.stdout
    assert "verification=passed" in apply_result.stdout

    assert (project / ".ai-engineering.toml").read_text(encoding="utf-8") == V2_MARKER
    gitignore = (project / ".gitignore").read_text(encoding="utf-8")
    assert ".pytest_cache/\n" in gitignore
    assert ".mypy_cache/\n" in gitignore
    assert ".ruff_cache/\n" in gitignore

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
    assert set(
        _run(
            ["git", "status", "--short"],
            cwd=project,
            environment=environment,
        ).stdout.splitlines()
    ) == {" M .gitignore", "?? .ai-engineering.toml"}

    plan_after = _run(
        _migration_command(cli, "plan", project),
        cwd=isolated,
        environment=environment,
    )
    assert "source_baseline=python-engineering-v2" in plan_after.stdout
    assert "operation_count=0" in plan_after.stdout
    assert "manual_review_count=0" in plan_after.stdout
    assert "status=already_target" in plan_after.stdout

    apply_again = _run(
        _migration_command(cli, "apply", project),
        cwd=isolated,
        environment=environment,
    )
    assert "changed_count=0" in apply_again.stdout
    assert "verification=passed" in apply_again.stdout

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
