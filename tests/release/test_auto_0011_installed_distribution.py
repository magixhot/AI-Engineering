from __future__ import annotations

import json
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
        "status": _run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=root,
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
            project_name="Installed Approval Fixture",
            project_description="AUTO-0011-05 isolated wheel fixture.",
            author="AI-Engineering Test",
            include_python_scaffold=True,
        )
    )
    _commit_baseline(project)
    return project


def _approval(venv: Path, project: Path, cwd: Path) -> str:
    result = _cli(
        venv,
        ["project", "reconcile", "approve", "--project", str(project)],
        cwd=cwd,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["scope"] == "single_candidate"
    assert payload["version"] == 1
    assert len(payload["digest"]) == 64
    return result.stdout


def test_auto_0011_installed_approve_is_deterministic_and_read_only(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "approval-project")
    before = _git_snapshot(project)

    first = _approval(venv, project, tmp_path)
    second = _approval(venv, project, tmp_path)

    assert first == second
    assert first.endswith("\n")
    assert _git_snapshot(project) == before


def test_auto_0011_installed_matching_approval_allows_only_bound_candidate(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "matching-project")
    approval = tmp_path / "approval.json"
    approval.write_text(_approval(venv, project, tmp_path), encoding="utf-8")
    before_head = _git_snapshot(project)["head"]

    result = _cli(
        venv,
        [
            "project",
            "reconcile",
            "run",
            "--project",
            str(project),
            "--approval",
            str(approval),
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 1
    assert result.stderr == ""
    assert "state=approval_refused" in result.stdout
    assert "successful_steps=1" in result.stdout
    assert "attempt_count=1" in result.stdout
    assert "Traceback" not in result.stdout
    assert _git_snapshot(project)["head"] == before_head


def test_auto_0011_installed_stale_approval_refuses_before_write(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "stale-project")
    approval = tmp_path / "approval.json"
    approval.write_text(_approval(venv, project, tmp_path), encoding="utf-8")
    _run(["git", "switch", "-c", "approval-drift"], cwd=project)
    before = _git_snapshot(project)

    result = _cli(
        venv,
        [
            "project",
            "reconcile",
            "run",
            "--project",
            str(project),
            "--approval",
            str(approval),
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 1
    assert result.stderr == ""
    assert "state=approval_refused" in result.stdout
    assert "successful_steps=0" in result.stdout
    assert "attempt_count=0" in result.stdout
    assert "issue=APPROVAL_GIT_MISMATCH:" in result.stdout
    assert "Traceback" not in result.stdout
    assert _git_snapshot(project) == before


def test_auto_0011_installed_malformed_approval_fails_closed(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "malformed-project")
    approval = tmp_path / "malformed-approval.json"
    approval.write_text("{", encoding="utf-8")
    before = _git_snapshot(project)

    result = _cli(
        venv,
        [
            "project",
            "reconcile",
            "run",
            "--project",
            str(project),
            "--approval",
            str(approval),
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 1
    assert result.stderr == ""
    assert "state=approval_error" in result.stdout
    assert "successful_steps=0" in result.stdout
    assert "attempt_count=0" in result.stdout
    assert "issue=APPROVAL_PARSE_ERROR:" in result.stdout
    assert "Traceback" not in result.stdout
    assert _git_snapshot(project) == before
