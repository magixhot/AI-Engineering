from __future__ import annotations

import hashlib
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
            project_name="Installed Receipt Fixture",
            project_description="AUTO-0012-05 isolated wheel fixture.",
            author="AI-Engineering Test",
            include_python_scaffold=True,
        )
    )
    _commit_baseline(project)
    return project


def _receipt(
    venv: Path,
    project: Path,
    cwd: Path,
    *extra: str,
) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
    result = _cli(
        venv,
        [
            "project",
            "reconcile",
            "run",
            "--project",
            str(project),
            "--receipt-json",
            *extra,
        ],
        cwd=cwd,
    )
    assert result.stderr == ""
    assert result.stdout.endswith("\n")
    assert "Traceback" not in result.stdout
    payload = json.loads(result.stdout)
    assert payload["version"] == 1
    assert payload["kind"] == "reconciliation_execution"
    assert isinstance(payload["digest"], str)
    assert len(payload["digest"]) == 64
    digest = payload.pop("digest")
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    assert digest == hashlib.sha256(canonical).hexdigest()
    payload["digest"] = digest
    assert str(project.resolve()) not in result.stdout
    return result, payload


def _approval(venv: Path, project: Path, cwd: Path) -> dict[str, object]:
    result = _cli(
        venv,
        ["project", "reconcile", "approve", "--project", str(project)],
        cwd=cwd,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    return json.loads(result.stdout)


def test_auto_0012_installed_receipt_records_real_delegated_execution(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "applied-project")
    before_head = _git_snapshot(project)["head"]

    result, payload = _receipt(
        venv,
        project,
        tmp_path,
        "--max-steps",
        "1",
    )

    assert result.returncode in {0, 1}
    attempts = payload["attempts"]
    assert isinstance(attempts, list)
    assert attempts
    first = attempts[0]
    assert isinstance(first, dict)
    assert first["state"] == "applied"
    assert first["write_attempted"] is True
    assert payload["successful_steps"] == 1
    assert payload["git_head"] == before_head
    assert payload["terminal_state"] in {"complete", "limit_reached"}
    assert _git_snapshot(project)["head"] == before_head


def test_auto_0012_installed_no_change_receipt_is_deterministic_and_read_only(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "clean-project")
    prepared = _cli(
        venv,
        ["project", "reconcile", "run", "--project", str(project)],
        cwd=tmp_path,
    )
    assert prepared.returncode == 0
    before = _git_snapshot(project)

    first, first_payload = _receipt(venv, project, tmp_path)
    second, second_payload = _receipt(venv, project, tmp_path)

    assert first.returncode == 0
    assert second.returncode == 0
    assert first.stdout == second.stdout
    assert first_payload == second_payload
    assert first_payload["terminal_state"] == "no_change"
    assert first_payload["attempts"] == []
    assert _git_snapshot(project) == before


def test_auto_0012_installed_policy_refusal_is_evidence_only_and_zero_write(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "policy-project")
    policy = tmp_path / "policy.toml"
    policy.write_text(
        "\n".join(
            [
                "version = 1",
                "denied_workflows = [",
                '  "project migrate plan --migration python-engineering-v1-to-v2",',
                '  "project docs ownership plan",',
                '  "project docs plan",',
                "]",
                "",
            ]
        ),
        encoding="utf-8",
    )
    before = _git_snapshot(project)

    result, payload = _receipt(
        venv,
        project,
        tmp_path,
        "--policy",
        str(policy),
    )

    assert result.returncode == 1
    assert payload["terminal_state"] == "policy_refused"
    assert payload["attempts"] == []
    assert payload["successful_steps"] == 0
    assert isinstance(payload["policy_fingerprint"], str)
    assert str(payload["policy_fingerprint"]).startswith("policy-sha256:")
    decisions = payload["policy_decisions"]
    assert isinstance(decisions, list)
    assert len(decisions) == 1
    assert isinstance(decisions[0], dict)
    assert decisions[0]["state"] == "policy_refused"
    assert _git_snapshot(project) == before


def test_auto_0012_installed_stale_approval_receipt_refuses_before_write(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "approval-project")
    approval_payload = _approval(venv, project, tmp_path)
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(approval_payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    _run(["git", "switch", "-c", "receipt-approval-drift"], cwd=project)
    before = _git_snapshot(project)

    result, payload = _receipt(
        venv,
        project,
        tmp_path,
        "--approval",
        str(approval),
    )

    assert result.returncode == 1
    assert payload["terminal_state"] == "approval_refused"
    assert payload["attempts"] == []
    assert payload["successful_steps"] == 0
    assert payload["approval_digest"] == approval_payload["digest"]
    assert payload["approval_scope"] == "single_candidate"
    verifications = payload["approval_verifications"]
    assert isinstance(verifications, list)
    assert verifications
    assert isinstance(verifications[0], dict)
    assert verifications[0]["state"] == "approval_refused"
    assert _git_snapshot(project) == before


def test_auto_0012_installed_malformed_approval_is_terminal_error_evidence(
    tmp_path: Path,
) -> None:
    venv = _build_installed_cli(tmp_path)
    project = _legacy_project(tmp_path, "approval-error-project")
    approval = tmp_path / "malformed-approval.json"
    approval.write_text("{", encoding="utf-8")
    before = _git_snapshot(project)

    result, payload = _receipt(
        venv,
        project,
        tmp_path,
        "--approval",
        str(approval),
    )

    assert result.returncode == 1
    assert payload["terminal_state"] == "approval_error"
    assert payload["attempts"] == []
    assert payload["successful_steps"] == 0
    assert payload["approval_digest"] is None
    assert payload["approval_scope"] is None
    terminal_issues = payload["terminal_issues"]
    assert isinstance(terminal_issues, list)
    assert any(
        isinstance(issue, dict) and issue.get("code") == "APPROVAL_PARSE_ERROR"
        for issue in terminal_issues
    )
    assert _git_snapshot(project) == before
