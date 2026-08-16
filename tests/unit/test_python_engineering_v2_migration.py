from __future__ import annotations

import subprocess
from pathlib import Path

from ai_engineering.project_migration import (
    PYTHON_ENGINEERING_V1_BASELINE,
    PYTHON_ENGINEERING_V1_TO_V2_MIGRATION,
    ProjectMigrationRequest,
    detect_project_identity,
    plan_project_migration,
)
from ai_engineering.project_migration_apply import apply_project_migration
from ai_engineering.project_templates import (
    StandaloneProjectRequest,
    create_standalone_project,
)
from ai_engineering.python_engineering_baseline import (
    PYTHON_ENGINEERING_IDENTITY_PATH,
    PYTHON_ENGINEERING_V2_BASELINE,
    PYTHON_ENGINEERING_V2_GITIGNORE,
    PYTHON_ENGINEERING_V2_IDENTITY,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.rstrip("\r\n")


def _legacy_v1_project(tmp_path: Path) -> Path:
    root = tmp_path / "legacy-v1"
    create_standalone_project(
        StandaloneProjectRequest(
            target_directory=root,
            project_name="Legacy V1",
            project_description="Production migration fixture.",
            author="Example Maintainer",
            include_python_scaffold=True,
        )
    )
    _git(root, "init")
    _git(root, "config", "user.name", "Test User")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "--allow-empty", "-m", "baseline")
    return root


def test_production_v1_to_v2_migration_is_guarded_and_idempotent(
    tmp_path: Path,
) -> None:
    root = _legacy_v1_project(tmp_path)
    identity_before = detect_project_identity(root)
    head_before = _git(root, "rev-parse", "HEAD")
    index_before = _git(root, "diff", "--cached", "--binary")

    assert identity_before.baseline == PYTHON_ENGINEERING_V1_BASELINE

    request = ProjectMigrationRequest(
        project_root=root,
        migration_id=PYTHON_ENGINEERING_V1_TO_V2_MIGRATION,
    )
    first_plan = plan_project_migration(request)

    assert first_plan.source_baseline == PYTHON_ENGINEERING_V1_BASELINE
    assert first_plan.target_baseline == PYTHON_ENGINEERING_V2_BASELINE
    assert first_plan.manual_review == ()
    assert tuple(item.path for item in first_plan.operations) == (
        ".ai-engineering.toml",
        ".gitignore",
    )

    result = apply_project_migration(first_plan)

    assert result.target_baseline == PYTHON_ENGINEERING_V2_BASELINE
    assert result.changed_paths == (
        ".ai-engineering.toml",
        ".gitignore",
    )
    assert (root / PYTHON_ENGINEERING_IDENTITY_PATH).read_text(
        encoding="utf-8"
    ) == PYTHON_ENGINEERING_V2_IDENTITY
    assert (root / ".gitignore").read_text(
        encoding="utf-8"
    ) == PYTHON_ENGINEERING_V2_GITIGNORE
    assert detect_project_identity(root).baseline == PYTHON_ENGINEERING_V2_BASELINE
    assert _git(root, "rev-parse", "HEAD") == head_before
    assert _git(root, "diff", "--cached", "--binary") == index_before

    second_plan = plan_project_migration(request)

    assert second_plan.source_baseline == PYTHON_ENGINEERING_V2_BASELINE
    assert second_plan.target_baseline == PYTHON_ENGINEERING_V2_BASELINE
    assert second_plan.operations == ()
    assert second_plan.manual_review == ()
    second_result = apply_project_migration(second_plan)
    assert second_result.changed_paths == ()
    assert _git(root, "rev-parse", "HEAD") == head_before
    assert _git(root, "diff", "--cached", "--binary") == index_before
