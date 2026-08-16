from __future__ import annotations

from pathlib import Path

from ai_engineering.project_git_readiness import ProjectGitReadiness
from ai_engineering.project_health import (
    NEXT_DOCS_PLAN,
    NEXT_MIGRATION_PLAN,
    NEXT_OWNERSHIP_PLAN,
)
from ai_engineering.project_reconciliation_policy import (
    evaluate_reconciliation_policy,
    load_reconciliation_policy,
)


def _git(
    *,
    branch: str | None = "main",
    staged: tuple[str, ...] = (),
    unstaged: tuple[str, ...] = (),
    untracked: tuple[str, ...] = (),
) -> ProjectGitReadiness:
    return ProjectGitReadiness(
        repository=True,
        branch=branch,
        head="abc123",
        staged_paths=staged,
        unstaged_paths=unstaged,
        untracked_paths=untracked,
    )


def _policy(tmp_path: Path, body: str):
    path = tmp_path / "policy.toml"
    path.write_text(body, encoding="utf-8")
    return load_reconciliation_policy(path)


def test_loads_minimal_policy_with_preserving_defaults(tmp_path: Path) -> None:
    loaded = _policy(tmp_path, "version = 1\n")

    assert loaded.state == "loaded"
    assert loaded.policy is not None
    assert loaded.policy.max_steps is None
    assert loaded.policy.allow_dirty_worktree is True
    assert loaded.policy.allow_untracked_files is True
    assert loaded.policy.require_attached_branch is False
    assert loaded.policy.allowed_workflows == ()
    assert loaded.policy.denied_workflows == ()


def test_unknown_field_fails_closed(tmp_path: Path) -> None:
    loaded = _policy(tmp_path, "version = 1\nmagic = true\n")

    assert loaded.state == "policy_error"
    assert loaded.policy is None
    assert [issue.code for issue in loaded.issues] == ["POLICY_UNKNOWN_FIELD"]


def test_unknown_workflow_fails_closed(tmp_path: Path) -> None:
    loaded = _policy(
        tmp_path,
        'version = 1\nallowed_workflows = ["made-up-workflow"]\n',
    )

    assert loaded.state == "policy_error"
    assert [issue.code for issue in loaded.issues] == ["POLICY_UNKNOWN_WORKFLOW"]


def test_contradictory_allow_and_deny_fails_closed(tmp_path: Path) -> None:
    loaded = _policy(
        tmp_path,
        "\n".join(
            [
                "version = 1",
                f"allowed_workflows = [{NEXT_DOCS_PLAN!r}]",
                f"denied_workflows = [{NEXT_DOCS_PLAN!r}]",
            ]
        ),
    )

    assert loaded.state == "policy_error"
    assert [issue.code for issue in loaded.issues] == [
        "POLICY_CONTRADICTORY_WORKFLOW"
    ]


def test_policy_only_allows_existing_workflow_identity(tmp_path: Path) -> None:
    loaded = _policy(
        tmp_path,
        "\n".join(
            [
                "version = 1",
                f"allowed_workflows = [{NEXT_DOCS_PLAN!r}]",
            ]
        ),
    )

    allowed = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_git(),
        project_root=tmp_path,
    )
    refused = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_OWNERSHIP_PLAN,
        git_readiness=_git(),
        project_root=tmp_path,
    )

    assert allowed.state == "allowed"
    assert allowed.issues == ()
    assert refused.state == "policy_refused"
    assert [issue.code for issue in refused.issues] == [
        "POLICY_WORKFLOW_NOT_ALLOWED"
    ]


def test_explicit_deny_refuses_candidate(tmp_path: Path) -> None:
    loaded = _policy(
        tmp_path,
        "\n".join(
            [
                "version = 1",
                f"denied_workflows = [{NEXT_MIGRATION_PLAN!r}]",
            ]
        ),
    )

    decision = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_MIGRATION_PLAN,
        git_readiness=_git(),
        project_root=tmp_path,
    )

    assert decision.state == "policy_refused"
    assert [issue.code for issue in decision.issues] == ["POLICY_WORKFLOW_DENIED"]


def test_git_constraints_are_deterministic_and_fail_closed(tmp_path: Path) -> None:
    loaded = _policy(
        tmp_path,
        "\n".join(
            [
                "version = 1",
                "allow_dirty_worktree = false",
                "allow_untracked_files = false",
                "require_attached_branch = true",
            ]
        ),
    )

    decision = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_git(
            branch=None,
            staged=("a.py",),
            unstaged=("b.py",),
            untracked=("c.py",),
        ),
        project_root=tmp_path,
    )

    assert decision.state == "policy_refused"
    assert [issue.code for issue in decision.issues] == [
        "POLICY_DETACHED_BRANCH",
        "POLICY_DIRTY_WORKTREE",
        "POLICY_UNTRACKED_FILES",
    ]
    assert decision.staged_paths == ("a.py",)
    assert decision.unstaged_paths == ("b.py",)
    assert decision.untracked_paths == ("c.py",)


def test_stricter_progress_limit_wins(tmp_path: Path) -> None:
    loaded = _policy(tmp_path, "version = 1\nmax_steps = 4\n")

    policy_stricter = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_git(),
        project_root=tmp_path,
        requested_max_steps=8,
    )
    caller_stricter = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_git(),
        project_root=tmp_path,
        requested_max_steps=2,
    )

    assert policy_stricter.effective_max_steps == 4
    assert caller_stricter.effective_max_steps == 2


def test_root_match_requires_exact_explicit_root(tmp_path: Path) -> None:
    loaded = _policy(tmp_path, "version = 1\nrequire_project_root_match = true\n")
    project = tmp_path / "project"
    other = tmp_path / "other"
    project.mkdir()
    other.mkdir()

    missing = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_git(),
        project_root=project,
    )
    mismatch = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_git(),
        project_root=project,
        expected_project_root=other,
    )

    assert missing.state == "policy_error"
    assert [issue.code for issue in missing.issues] == [
        "POLICY_PROJECT_ROOT_UNAVAILABLE"
    ]
    assert mismatch.state == "policy_refused"
    assert [issue.code for issue in mismatch.issues] == [
        "POLICY_PROJECT_ROOT_MISMATCH"
    ]


def test_malformed_and_unreadable_policy_return_typed_errors(tmp_path: Path) -> None:
    malformed_path = tmp_path / "malformed.toml"
    malformed_path.write_text("version = [", encoding="utf-8")

    malformed = load_reconciliation_policy(malformed_path)
    missing = load_reconciliation_policy(tmp_path / "missing.toml")

    assert malformed.state == "policy_error"
    assert [issue.code for issue in malformed.issues] == ["POLICY_PARSE_ERROR"]
    assert missing.state == "policy_error"
    assert [issue.code for issue in missing.issues] == ["POLICY_UNREADABLE"]


def test_invalid_loaded_policy_produces_policy_error_decision(tmp_path: Path) -> None:
    loaded = _policy(tmp_path, "version = 2\n")

    decision = evaluate_reconciliation_policy(
        loaded,
        workflow=NEXT_DOCS_PLAN,
        git_readiness=_git(),
        project_root=tmp_path,
        requested_max_steps=8,
    )

    assert decision.state == "policy_error"
    assert decision.effective_max_steps == 8
    assert [issue.code for issue in decision.issues] == [
        "POLICY_VERSION_UNSUPPORTED"
    ]
