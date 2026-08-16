from __future__ import annotations

import subprocess
from pathlib import Path

from ai_engineering.project_reconciliation import plan_project_reconciliation
from ai_engineering.project_reconciliation_approval import (
    serialize_reconciliation_approval,
)
from ai_engineering.project_reconciliation_approval_context import (
    build_approval_for_plan,
)
from ai_engineering.project_reconciliation_orchestration import (
    run_project_reconciliation,
)
from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
        shell=False,
        stdin=subprocess.DEVNULL,
    ).stdout.rstrip("\r\n")


def _bootstrap_v1(tmp_path: Path) -> Path:
    root = tmp_path / "legacy-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=root,
            project_name="Legacy Project",
            project_description="AUTO-0011 approval integration fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    _git(root, "config", "user.name", "Test User")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "add", "-A")
    _git(root, "commit", "--allow-empty", "-m", "baseline")
    return root


def _approval_file(
    tmp_path: Path,
    root: Path,
    *,
    policy_path: Path | None = None,
) -> Path:
    approval = build_approval_for_plan(
        plan_project_reconciliation(root),
        policy_path=policy_path,
    )
    path = tmp_path / "approval.json"
    path.write_bytes(serialize_reconciliation_approval(approval))
    return path


def test_matching_approval_allows_only_bound_candidate(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)
    approval_path = _approval_file(tmp_path, root)

    result = run_project_reconciliation(root, approval_path=approval_path)

    assert result.state == "approval_refused"
    assert result.successful_steps == 1
    assert len(result.attempts) == 1
    assert result.attempts[0].state == "applied"
    assert result.issues
    assert result.issues[0].code in {
        "APPROVAL_CANDIDATE_MISMATCH",
        "APPROVAL_PROJECT_MISMATCH",
    }


def test_stale_approval_refuses_before_any_write(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)
    approval_path = _approval_file(tmp_path, root)
    before_head = _git(root, "rev-parse", "HEAD")
    before_status = _git(root, "status", "--porcelain=v1")
    _git(root, "switch", "-c", "approval-drift")

    result = run_project_reconciliation(root, approval_path=approval_path)

    assert result.state == "approval_refused"
    assert result.successful_steps == 0
    assert result.attempts == ()
    assert [issue.code for issue in result.issues] == ["APPROVAL_GIT_MISMATCH"]
    assert _git(root, "rev-parse", "HEAD") == before_head
    assert _git(root, "status", "--porcelain=v1") == before_status


def test_policy_drift_invalidates_matching_candidate_approval(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)
    policy = tmp_path / "policy.toml"
    policy.write_text("version = 1\nmax_steps = 8\n", encoding="utf-8")
    approval_path = _approval_file(tmp_path, root, policy_path=policy)
    before_status = _git(root, "status", "--porcelain=v1")

    policy.write_text("version = 1\nmax_steps = 1\n", encoding="utf-8")
    result = run_project_reconciliation(
        root,
        policy_path=policy,
        approval_path=approval_path,
    )

    assert result.state == "approval_refused"
    assert result.successful_steps == 0
    assert result.attempts == ()
    assert [issue.code for issue in result.issues] == ["APPROVAL_POLICY_MISMATCH"]
    assert _git(root, "status", "--porcelain=v1") == before_status


def test_malformed_approval_fails_before_candidate_write(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)
    approval_path = tmp_path / "approval.json"
    approval_path.write_text("{", encoding="utf-8")
    before_status = _git(root, "status", "--porcelain=v1")

    result = run_project_reconciliation(root, approval_path=approval_path)

    assert result.state == "approval_error"
    assert result.successful_steps == 0
    assert result.attempts == ()
    assert result.issues[0].code == "APPROVAL_PARSE_ERROR"
    assert _git(root, "status", "--porcelain=v1") == before_status
