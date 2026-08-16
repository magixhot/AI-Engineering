from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from ai_engineering.project_health import NEXT_MIGRATION_PLAN
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


def _legacy_project(tmp_path: Path, name: str) -> Path:
    project = tmp_path / name
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=project,
            project_name="Installed Policy Fixture",
            project_description="AUTO-0010-05 isolated wheel fixture.",
            author="AI-Engineering Test",
            include_python_scaffold=True,
        )
    )
    _commit_baseline(project)
    return project


def test_auto_0010_installed_policy_refuses_before_first_write(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "denied-project")
    policy = tmp_path / "deny.toml"
    policy.write_text(
        "\n".join(
            [
                "version = 1",
                f"denied_workflows = [{NEXT_MIGRATION_PLAN!r}]",
                "",
            ]
        ),
        encoding="utf-8",
    )
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
            "--policy",
            str(policy),
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
    assert "state=policy_refused" in result.stdout
    assert "successful_steps=0" in result.stdout
    assert "attempt_count=0" in result.stdout
    assert "policy_decision_count=1" in result.stdout
    assert "policy_issue=POLICY_WORKFLOW_DENIED:" in result.stdout
    assert "Traceback" not in result.stdout
    assert after == before


def test_auto_0010_installed_policy_limit_is_stricter_than_cli(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "limited-project")
    policy = tmp_path / "limit.toml"
    policy.write_text("version = 1\nmax_steps = 1\n", encoding="utf-8")
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
            "8",
            "--policy",
            str(policy),
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 1
    assert result.stderr == ""
    assert "state=limit_reached" in result.stdout
    assert "successful_steps=1" in result.stdout
    assert "attempt_count=1" in result.stdout
    assert "policy_decision_count=2" in result.stdout
    assert result.stdout.count(":allowed:1") == 2
    assert "issue=PROGRESS_LIMIT_REACHED:" in result.stdout
    assert "Traceback" not in result.stdout
    assert _git_snapshot(project) == before


def test_auto_0010_installed_malformed_policy_fails_closed(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "malformed-project")
    policy = tmp_path / "malformed.toml"
    policy.write_text("version = [\n", encoding="utf-8")
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
            "--policy",
            str(policy),
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
    assert "state=policy_error" in result.stdout
    assert "successful_steps=0" in result.stdout
    assert "attempt_count=0" in result.stdout
    assert "policy_decision_count=1" in result.stdout
    assert "policy_issue=POLICY_PARSE_ERROR:" in result.stdout
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert after == before
