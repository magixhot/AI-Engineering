from __future__ import annotations

import subprocess
from pathlib import Path

from ai_engineering.project_git_readiness import inspect_project_git_readiness
from ai_engineering.project_health import NEXT_DOCS_PLAN, NEXT_MIGRATION_PLAN
from ai_engineering.project_reconciliation_policy import (
    evaluate_reconciliation_policy,
    load_reconciliation_policy,
)


def _run(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    _run(root, "init", "-b", "main")
    _run(root, "config", "user.name", "AUTO-0010 Tests")
    _run(root, "config", "user.email", "auto0010@example.invalid")
    (root / "README.md").write_text("baseline\n", encoding="utf-8")
    _run(root, "add", "README.md")
    _run(root, "commit", "-m", "baseline")
    return root


def _readiness(root: Path):
    return inspect_project_git_readiness(
        root,
        repository=True,
        branch=_run(root, "branch", "--show-current") or None,
        head=_run(root, "rev-parse", "HEAD"),
    )


def _git_snapshot(root: Path) -> tuple[str, str, str, str, str]:
    return (
        _run(root, "rev-parse", "HEAD"),
        _run(root, "branch", "--show-current"),
        _run(root, "diff", "--cached", "--name-only"),
        _run(root, "remote", "-v"),
        _run(root, "config", "--local", "--list"),
    )


def test_duplicate_toml_semantics_fail_closed(tmp_path: Path) -> None:
    policy = tmp_path / "policy.toml"
    policy.write_text("version = 1\nversion = 1\n", encoding="utf-8")

    loaded = load_reconciliation_policy(policy)

    assert loaded.state == "policy_error"
    assert loaded.policy is None
    assert [issue.code for issue in loaded.issues] == ["POLICY_PARSE_ERROR"]


def test_equivalent_policy_order_produces_identical_decision(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    first_path = tmp_path / "first.toml"
    second_path = tmp_path / "second.toml"
    first_path.write_text(
        "\n".join(
            [
                "version = 1",
                "max_steps = 4",
                "allow_dirty_worktree = false",
                "allow_untracked_files = false",
                f"denied_workflows = [{NEXT_MIGRATION_PLAN!r}]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    second_path.write_text(
        "\n".join(
            [
                f"denied_workflows = [{NEXT_MIGRATION_PLAN!r}]",
                "allow_untracked_files = false",
                "version = 1",
                "allow_dirty_worktree = false",
                "max_steps = 4",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    first = evaluate_reconciliation_policy(
        load_reconciliation_policy(first_path),
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_readiness(root),
        project_root=root,
        requested_max_steps=8,
    )
    second = evaluate_reconciliation_policy(
        load_reconciliation_policy(second_path),
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_readiness(root),
        project_root=root,
        requested_max_steps=8,
    )

    assert first.state == second.state == "allowed"
    assert first.workflow == second.workflow
    assert first.effective_max_steps == second.effective_max_steps == 4
    assert first.issues == second.issues == ()
    assert first.git_branch == second.git_branch == "main"
    assert first.staged_paths == second.staged_paths == ()
    assert first.unstaged_paths == second.unstaged_paths == ()
    assert first.untracked_paths == second.untracked_paths == ()


def test_policy_mutation_requires_fresh_reload_to_change_decision(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    policy_path = tmp_path / "policy.toml"
    policy_path.write_text("version = 1\n", encoding="utf-8")
    loaded_before = load_reconciliation_policy(policy_path)

    before = evaluate_reconciliation_policy(
        loaded_before,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_readiness(root),
        project_root=root,
    )

    policy_path.write_text(
        "\n".join(
            [
                "version = 1",
                f"denied_workflows = [{NEXT_DOCS_PLAN!r}]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    stale_loaded = evaluate_reconciliation_policy(
        loaded_before,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_readiness(root),
        project_root=root,
    )
    fresh_loaded = evaluate_reconciliation_policy(
        load_reconciliation_policy(policy_path),
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_readiness(root),
        project_root=root,
    )

    assert before.state == "allowed"
    assert stale_loaded.state == "allowed"
    assert fresh_loaded.state == "policy_refused"
    assert [issue.code for issue in fresh_loaded.issues] == [
        "POLICY_WORKFLOW_DENIED"
    ]


def test_dirty_staged_and_untracked_refusal_is_zero_write(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "README.md").write_text("changed\n", encoding="utf-8")
    (root / "staged.txt").write_text("staged\n", encoding="utf-8")
    _run(root, "add", "staged.txt")
    (root / "untracked.txt").write_text("untracked\n", encoding="utf-8")

    policy = tmp_path / "policy.toml"
    policy.write_text(
        "\n".join(
            [
                "version = 1",
                "allow_dirty_worktree = false",
                "allow_untracked_files = false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    readiness = _readiness(root)
    before = _git_snapshot(root)
    file_bytes = {
        path.name: path.read_bytes()
        for path in (root / "README.md", root / "staged.txt", root / "untracked.txt")
    }

    decision = evaluate_reconciliation_policy(
        load_reconciliation_policy(policy),
        workflow=NEXT_DOCS_PLAN,
        git_readiness=readiness,
        project_root=root,
    )

    after = _git_snapshot(root)
    assert decision.state == "policy_refused"
    assert [issue.code for issue in decision.issues] == [
        "POLICY_DIRTY_WORKTREE",
        "POLICY_UNTRACKED_FILES",
    ]
    assert decision.staged_paths == ("staged.txt",)
    assert decision.unstaged_paths == ("README.md",)
    assert decision.untracked_paths == ("untracked.txt",)
    assert after == before
    for name, expected in file_bytes.items():
        assert (root / name).read_bytes() == expected


def test_detached_branch_refusal_preserves_head_and_config(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    head = _run(root, "rev-parse", "HEAD")
    _run(root, "checkout", "--detach", head)
    policy = tmp_path / "policy.toml"
    policy.write_text(
        "version = 1\nrequire_attached_branch = true\n",
        encoding="utf-8",
    )
    before = _git_snapshot(root)

    decision = evaluate_reconciliation_policy(
        load_reconciliation_policy(policy),
        workflow=NEXT_DOCS_PLAN,
        git_readiness=inspect_project_git_readiness(
            root,
            repository=True,
            branch=None,
            head=head,
        ),
        project_root=root,
    )

    assert decision.state == "policy_refused"
    assert [issue.code for issue in decision.issues] == [
        "POLICY_DETACHED_BRANCH"
    ]
    assert _git_snapshot(root) == before


def test_unknown_candidate_is_error_even_when_policy_would_otherwise_allow(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    policy = tmp_path / "policy.toml"
    policy.write_text("version = 1\n", encoding="utf-8")

    decision = evaluate_reconciliation_policy(
        load_reconciliation_policy(policy),
        workflow="project unknown apply",
        git_readiness=_readiness(root),
        project_root=root,
    )

    assert decision.state == "policy_error"
    assert [issue.code for issue in decision.issues] == [
        "POLICY_UNKNOWN_CANDIDATE"
    ]


def test_invalid_requested_limit_fails_closed_deterministically(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    policy = tmp_path / "policy.toml"
    policy.write_text("version = 1\nmax_steps = 4\n", encoding="utf-8")
    loaded = load_reconciliation_policy(policy)

    first = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_readiness(root),
        project_root=root,
        requested_max_steps=0,
    )
    second = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_readiness(root),
        project_root=root,
        requested_max_steps=0,
    )

    assert first == second
    assert first.state == "policy_error"
    assert first.effective_max_steps == 0
    assert [issue.code for issue in first.issues] == [
        "POLICY_REQUEST_LIMIT_INVALID"
    ]
