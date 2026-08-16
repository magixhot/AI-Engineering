from __future__ import annotations

import subprocess
from pathlib import Path

from ai_engineering.documentation_ownership import (
    apply_documentation_ownership_initialization,
    plan_documentation_ownership_initialization,
)
from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_health import (
    NEXT_DOCS_PLAN,
    NEXT_MIGRATION_PLAN,
    NEXT_OWNERSHIP_PLAN,
)
from ai_engineering.project_inspection import (
    ProjectInspectionRequest,
    inspect_project_state,
)
from ai_engineering.project_migration import (
    PYTHON_ENGINEERING_V1_TO_V2_MIGRATION,
)
from ai_engineering.project_reconciliation import plan_project_reconciliation
from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)


def _bootstrap_v1(tmp_path: Path) -> Path:
    target = tmp_path / "legacy-project"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=target,
            project_name="Legacy Project",
            project_description="AUTO-0007 legacy fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    return target


def _bootstrap_v2(tmp_path: Path) -> Path:
    target = tmp_path / "v2-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=target,
            project_name="V2 Project",
            project_description="AUTO-0007 V2 fixture.",
            author="Example Maintainer",
        )
    )
    return target


def _initialize_ownership(root: Path) -> None:
    snapshot = inspect_project_state(ProjectInspectionRequest(root))
    ownership = plan_documentation_ownership_initialization(snapshot)
    assert not ownership.manual_review
    assert ownership.updates
    apply_documentation_ownership_initialization(ownership)


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=True,
        shell=False,
        stdin=subprocess.DEVNULL,
    )
    return result.stdout


def _project_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def _git_state(root: Path) -> dict[str, str]:
    return {
        "head": _git(root, "rev-parse", "HEAD"),
        "branch": _git(root, "branch", "--show-current"),
        "index": _git(root, "diff", "--cached", "--binary"),
        "status": _git(
            root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ),
        "remotes": _git(root, "remote", "-v"),
        "local_config": _git(root, "config", "--local", "--list"),
    }


def test_v1_plans_only_authoritative_migration_then_reinspection(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v1(tmp_path)

    plan = plan_project_reconciliation(root)

    assert plan.state == "ready"
    assert plan.health.next_action == NEXT_MIGRATION_PLAN
    assert plan.reinspect_required is True
    assert plan.expected_state == "reinspect_required"
    assert plan.issues == ()
    assert len(plan.steps) == 1
    assert plan.steps[0].sequence == 1
    assert plan.steps[0].workflow == plan.health.next_action
    assert plan.steps[0].migration_id == PYTHON_ENGINEERING_V1_TO_V2_MIGRATION
    assert plan.steps[0].affected_paths == ()
    assert plan.steps[0].reinspect_after_step is True


def test_v2_plans_ownership_initialization_with_bounded_paths(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v2(tmp_path)

    plan = plan_project_reconciliation(root)

    assert plan.state == "ready"
    assert plan.health.next_action == NEXT_OWNERSHIP_PLAN
    assert tuple(step.workflow for step in plan.steps) == (NEXT_OWNERSHIP_PLAN,)
    assert plan.steps[0].affected_paths == (
        "CURRENT_STATUS.md",
        "MASTER_INDEX.md",
        "PROJECT_MAP.md",
    )
    assert plan.steps[0].migration_id is None
    assert plan.steps[0].reinspect_after_step is True


def test_v2_with_initialized_drift_plans_only_documentation_sync(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v2(tmp_path)
    _initialize_ownership(root)
    (root / "notes.txt").write_text("observed drift\n", encoding="utf-8")

    plan = plan_project_reconciliation(root)

    assert plan.state == "ready"
    assert plan.health.next_action == NEXT_DOCS_PLAN
    assert tuple(step.workflow for step in plan.steps) == (NEXT_DOCS_PLAN,)
    assert plan.steps[0].affected_paths == ("PROJECT_MAP.md",)
    assert plan.steps[0].reinspect_after_step is True
    assert plan.expected_state == "reinspect_required"


def test_healthy_v2_project_is_clean_with_no_steps(tmp_path: Path) -> None:
    root = _bootstrap_v2(tmp_path)
    _initialize_ownership(root)

    plan = plan_project_reconciliation(root)

    assert plan.project_root == root.resolve()
    assert plan.state == "clean"
    assert plan.health.overall_state == "healthy"
    assert plan.steps == ()
    assert plan.issues == ()
    assert plan.reinspect_required is False
    assert plan.expected_state == "healthy"


def test_v1_ownership_blocker_fails_closed_without_unsafe_steps(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v1(tmp_path)
    (root / "CURRENT_STATUS.md").write_text(
        "<!-- ai-engineering:auto0002:current-status:start -->\n",
        encoding="utf-8",
    )

    plan = plan_project_reconciliation(root)

    assert plan.state == "manual_review"
    assert plan.health.overall_state == "manual_review"
    assert plan.steps == ()
    assert plan.reinspect_required is False
    assert plan.expected_state == "manual_review"
    assert tuple(issue.code for issue in plan.issues) == (
        "DOC_OWNERSHIP_PARTIAL",
    )


def test_v2_ownership_blockers_are_deterministic_and_ordered(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v2(tmp_path)
    (root / "CURRENT_STATUS.md").write_text(
        "<!-- ai-engineering:auto0002:current-status:start -->\n",
        encoding="utf-8",
    )
    (root / "MASTER_INDEX.md").write_text(
        "<!-- ai-engineering:auto0002:master-index:start -->\n"
        "<!-- ai-engineering:auto0002:master-index:start -->\n",
        encoding="utf-8",
    )

    first = plan_project_reconciliation(root)
    second = plan_project_reconciliation(root)

    assert first == second
    assert first.state == "manual_review"
    assert first.steps == ()
    assert first.expected_state == "manual_review"
    assert tuple((issue.code, issue.path) for issue in first.issues) == (
        ("DOC_OWNERSHIP_DUPLICATE", "MASTER_INDEX.md"),
        ("DOC_OWNERSHIP_PARTIAL", "CURRENT_STATUS.md"),
    )


def test_malformed_v2_marker_is_unsupported_without_v1_fallback(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v1(tmp_path)
    (root / ".ai-engineering.toml").write_text(
        'profile = "python-engineering"\nbaseline = "unapproved"\n',
        encoding="utf-8",
    )

    plan = plan_project_reconciliation(root)

    assert plan.state == "unsupported"
    assert plan.health.overall_state == "unsupported"
    assert plan.health.identity is None
    assert plan.steps == ()
    assert plan.reinspect_required is False
    assert plan.expected_state == "unsupported"
    assert tuple(issue.code for issue in plan.issues) == ("IDENTITY_UNSUPPORTED",)


def test_reconciliation_is_read_only_for_project_bytes_and_git_state(
    tmp_path: Path,
) -> None:
    root = _bootstrap_v2(tmp_path)
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\nstaged human change\n",
        encoding="utf-8",
    )
    _git(root, "add", "README.md")
    readme.write_text(
        readme.read_text(encoding="utf-8") + "unstaged human change\n",
        encoding="utf-8",
    )
    (root / "notes.txt").write_text("untracked\n", encoding="utf-8")
    _git(root, "remote", "add", "origin", "https://example.invalid/project.git")
    _git(root, "config", "auto0007.invariant", "preserved")
    bytes_before = _project_bytes(root)
    git_before = _git_state(root)

    first = plan_project_reconciliation(root)
    second = plan_project_reconciliation(root)

    assert first == second
    assert first.state == "ready"
    assert tuple(step.sequence for step in first.steps) == (1,)
    assert first.steps[0].affected_paths == tuple(
        sorted(first.steps[0].affected_paths)
    )
    assert _project_bytes(root) == bytes_before
    assert _git_state(root) == git_before
