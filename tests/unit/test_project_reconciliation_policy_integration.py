from __future__ import annotations

import subprocess
from pathlib import Path

from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_health import NEXT_DOCS_PLAN, NEXT_MIGRATION_PLAN
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


def _commit_baseline(root: Path) -> None:
    _git(root, "config", "user.name", "Test User")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "add", "-A")
    _git(root, "commit", "--allow-empty", "-m", "baseline")


def _bootstrap_v1(tmp_path: Path) -> Path:
    root = tmp_path / "legacy-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=root,
            project_name="Legacy Project",
            project_description="AUTO-0010 integration fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    _commit_baseline(root)
    return root


def _bootstrap_v2(tmp_path: Path) -> Path:
    root = tmp_path / "v2-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=root,
            project_name="V2 Project",
            project_description="AUTO-0010 V2 integration fixture.",
            author="Example Maintainer",
        )
    )
    _commit_baseline(root)
    return root


def _write_policy(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "policy.toml"
    path.write_text(body, encoding="utf-8")
    return path


def test_policy_denies_first_candidate_before_any_write(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)
    policy = _write_policy(
        tmp_path,
        "\n".join(
            [
                "version = 1",
                f"denied_workflows = [{NEXT_MIGRATION_PLAN!r}]",
                "",
            ]
        ),
    )
    head = _git(root, "rev-parse", "HEAD")
    status = _git(root, "status", "--porcelain=v1")

    result = run_project_reconciliation(root, policy_path=policy)

    assert result.state == "policy_refused"
    assert result.successful_steps == 0
    assert result.attempts == ()
    assert len(result.policy_decisions) == 1
    assert result.policy_decisions[0].state == "policy_refused"
    assert result.policy_decisions[0].workflow == NEXT_MIGRATION_PLAN
    assert result.issues[0].code == "POLICY_WORKFLOW_DENIED"
    assert _git(root, "rev-parse", "HEAD") == head
    assert _git(root, "status", "--porcelain=v1") == status


def test_policy_limit_is_stricter_than_cli_limit(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)
    policy = _write_policy(tmp_path, "version = 1\nmax_steps = 1\n")

    result = run_project_reconciliation(root, max_steps=8, policy_path=policy)

    assert result.state == "limit_reached"
    assert result.successful_steps == 1
    assert len(result.attempts) == 1
    assert len(result.policy_decisions) == 2
    assert all(item.state == "allowed" for item in result.policy_decisions)
    assert all(item.effective_max_steps == 1 for item in result.policy_decisions)
    assert result.issues[0].code == "PROGRESS_LIMIT_REACHED"


def test_later_policy_refusal_preserves_partial_progress(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v1(tmp_path)
    policy = _write_policy(
        tmp_path,
        "\n".join(
            [
                "version = 1",
                f"denied_workflows = [{NEXT_DOCS_PLAN!r}]",
                "",
            ]
        ),
    )

    result = run_project_reconciliation(root, policy_path=policy)

    assert result.state == "policy_refused"
    assert result.successful_steps >= 1
    assert len(result.attempts) == result.successful_steps
    assert result.policy_decisions[-1].state == "policy_refused"
    assert result.policy_decisions[-1].workflow == NEXT_DOCS_PLAN
    assert result.issues[0].code == "POLICY_WORKFLOW_DENIED"


def test_malformed_explicit_policy_fails_before_candidate_write(tmp_path: Path) -> None:
    root = _bootstrap_v1(tmp_path)
    policy = _write_policy(tmp_path, "version = [\n")
    head = _git(root, "rev-parse", "HEAD")

    result = run_project_reconciliation(root, policy_path=policy)

    assert result.state == "policy_error"
    assert result.successful_steps == 0
    assert result.attempts == ()
    assert len(result.policy_decisions) == 1
    assert result.policy_decisions[0].state == "policy_error"
    assert result.issues[0].code == "POLICY_PARSE_ERROR"
    assert _git(root, "rev-parse", "HEAD") == head


def test_no_policy_preserves_healthy_no_change_behavior(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v2(tmp_path)
    first = run_project_reconciliation(root)
    assert first.state == "complete"

    result = run_project_reconciliation(root)

    assert result.state == "no_change"
    assert result.policy_decisions == ()
