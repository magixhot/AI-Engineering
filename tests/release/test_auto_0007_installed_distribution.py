from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
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
        "status": _run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=root,
        ).stdout,
        "remotes": _run(["git", "remote", "-v"], cwd=root).stdout,
    }


def _make_git_project(root: Path) -> None:
    if (root / ".git").is_dir():
        return
    _run(["git", "init", "-b", "main"], cwd=root)
    _run(["git", "add", "."], cwd=root)
    _run(
        [
            "git",
            "-c",
            "user.name=AI-Engineering Test",
            "-c",
            "user.email=ai-engineering-test@example.invalid",
            "commit",
            "-m",
            "fixture",
        ],
        cwd=root,
    )


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


def test_auto_0007_public_cli_works_from_isolated_wheel(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = tmp_path / "v2-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=project,
            project_name="Installed Reconciliation Fixture",
            project_description="AUTO-0007-05 isolated wheel fixture.",
            author="AI-Engineering Test",
        )
    )
    _make_git_project(project)
    before = _git_snapshot(project)

    first = _cli(
        venv,
        ["project", "reconcile", "plan", "--project", str(project)],
        cwd=tmp_path,
    )
    second = _cli(
        venv,
        ["project", "reconcile", "plan", "--project", str(project)],
        cwd=tmp_path,
    )

    assert first.returncode == 0
    assert first.stderr == ""
    assert second.returncode == 0
    assert second.stdout == first.stdout
    assert "state=ready" in first.stdout
    assert "step=1:project docs ownership plan" in first.stdout
    assert "expected_state=reinspect_required" in first.stdout
    assert _git_snapshot(project) == before


def test_auto_0007_installed_cli_unsupported_is_controlled(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = tmp_path / "unsupported-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=project,
            project_name="Unsupported Fixture",
            project_description="AUTO-0007-05 unsupported fixture.",
            author="AI-Engineering Test",
            include_python_scaffold=True,
        )
    )
    (project / ".ai-engineering.toml").write_text(
        'profile = "python-engineering"\nbaseline = "unapproved"\n',
        encoding="utf-8",
    )
    _make_git_project(project)
    before = _git_snapshot(project)

    result = _cli(
        venv,
        ["project", "reconcile", "plan", "--project", str(project)],
        cwd=tmp_path,
    )

    assert result.returncode == 1
    assert result.stderr == ""
    assert "state=unsupported" in result.stdout
    assert "issue=IDENTITY_UNSUPPORTED:unsupported:" in result.stdout
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert _git_snapshot(project) == before
