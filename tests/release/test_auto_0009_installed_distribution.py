from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)


def _run(
    command: list[str], *, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        check=True,
    )


def _git_snapshot(root: Path) -> dict[str, str]:
    return {
        "head": _run(["git", "rev-parse", "HEAD"], cwd=root).stdout.strip(),
        "branch": _run(
            ["git", "branch", "--show-current"], cwd=root
        ).stdout.strip(),
        "index": _run(
            ["git", "diff", "--cached", "--name-only"], cwd=root
        ).stdout,
        "remotes": _run(["git", "remote", "-v"], cwd=root).stdout,
    }


def _commit_baseline(root: Path) -> None:
    _run(["git", "config", "user.name", "AI-Engineering Test"], cwd=root)
    _run(
        [
            "git",
            "config",
            "user.email",
            "ai-engineering-test@example.invalid",
        ],
        cwd=root,
    )
    _run(["git", "add", "-A"], cwd=root)
    _run(["git", "commit", "--allow-empty", "-m", "fixture"], cwd=root)


def _build_installed_cli(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    _run([sys.executable, "-m", "build", "--wheel", "--outdir", str(dist)])
    wheel_candidates = sorted(dist.glob("ai_engineering-*.whl"))
    assert len(wheel_candidates) == 1
    venv = tmp_path / "venv"
    _run([sys.executable, "-m", "venv", str(venv)])
    python = venv / "Scripts" / "python.exe"
    if not python.exists():
        python = venv / "bin" / "python"
    _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-deps",
            str(wheel_candidates[0]),
        ]
    )
    return venv


def _cli(
    venv: Path,
    args: list[str],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    executable = venv / "Scripts" / "ai-engineering.exe"
    if not executable.exists():
        executable = venv / "bin" / "ai-engineering"
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [str(executable), *args],
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def test_auto_0009_public_run_cli_completes_from_isolated_wheel(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = tmp_path / "legacy-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=project,
            project_name="Installed Orchestration Fixture",
            project_description="AUTO-0009-05 isolated wheel fixture.",
            author="AI-Engineering Test",
            include_python_scaffold=True,
        )
    )
    _commit_baseline(project)
    before = _git_snapshot(project)

    result = _cli(
        venv,
        [
            "project",
            "reconcile",
            "run",
            "--project",
            str(project),
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "state=complete" in result.stdout
    assert "successful_steps=" in result.stdout
    assert "attempt_count=" in result.stdout
    successful_steps = next(
        int(line.partition("=")[2])
        for line in result.stdout.splitlines()
        if line.startswith("successful_steps=")
    )
    attempt_count = next(
        int(line.partition("=")[2])
        for line in result.stdout.splitlines()
        if line.startswith("attempt_count=")
    )
    assert successful_steps >= 2
    assert attempt_count == successful_steps
    assert result.stdout.count("attempt=") == attempt_count
    assert "final_plan_state=clean" in result.stdout
    assert "Traceback" not in result.stdout
    assert _git_snapshot(project) == before
    assert _run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=project,
    ).stdout


def test_auto_0009_installed_run_cli_limit_is_bounded(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = tmp_path / "limited-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=project,
            project_name="Installed Limited Orchestration Fixture",
            project_description="AUTO-0009-05 bounded progress fixture.",
            author="AI-Engineering Test",
            include_python_scaffold=True,
        )
    )
    _commit_baseline(project)
    before = _git_snapshot(project)

    result = _cli(
        venv,
        [
            "project",
            "reconcile",
            "run",
            "--project",
            str(project),
            "--max-steps",
            "1",
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 1
    assert result.stderr == ""
    assert "state=limit_reached" in result.stdout
    assert "successful_steps=1" in result.stdout
    assert "attempt_count=1" in result.stdout
    assert "issue=PROGRESS_LIMIT_REACHED:" in result.stdout
    assert "final_plan_state=ready" in result.stdout
    assert "Traceback" not in result.stdout
    assert _git_snapshot(project) == before


def test_auto_0009_installed_run_cli_unsupported_is_zero_write(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = tmp_path / "unsupported-project"
    project.mkdir()
    _run(["git", "init", "-b", "main"], cwd=project)
    _commit_baseline(project)
    before = {
        **_git_snapshot(project),
        "status": _run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=project,
        ).stdout,
    }

    result = _cli(
        venv,
        [
            "project",
            "reconcile",
            "run",
            "--project",
            str(project),
        ],
        cwd=tmp_path,
    )

    after = {
        **_git_snapshot(project),
        "status": _run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=project,
        ).stdout,
    }
    assert result.returncode == 1
    assert result.stderr == ""
    assert "state=stopped" in result.stdout
    assert "successful_steps=0" in result.stdout
    assert "attempt_count=0" in result.stdout
    assert "issue=PLAN_UNSUPPORTED:" in result.stdout
    assert "final_plan_state=unsupported" in result.stdout
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert after == before
