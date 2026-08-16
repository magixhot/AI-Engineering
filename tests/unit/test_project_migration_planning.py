from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_migration import (
    ACTION_CREATE_FILE,
    ACTION_DELETE_MACHINE_FILE,
    ACTION_REPLACE_MACHINE_FILE,
    OWNERSHIP_GENERATED_ABSENT,
    OWNERSHIP_HUMAN,
    OWNERSHIP_MACHINE,
    OWNERSHIP_UNKNOWN,
    PYTHON_ENGINEERING_V1_BASELINE,
    STATE_ALREADY_TARGET,
    STATE_LOCALLY_MODIFIED,
    STATE_MANUAL_REVIEW,
    STATE_MISSING,
    STATE_OUTSIDE_ROOT,
    STATE_UNCHANGED_SOURCE,
    STATE_UNEXPECTED_PRESENT,
    STATE_UNSUPPORTED_TYPE,
    MigrationContract,
    MigrationPathRule,
    MigrationRegistry,
    ProjectMigrationRequest,
    plan_project_migration,
)


def _bootstrap(tmp_path: Path) -> Path:
    root = tmp_path / "sample-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=root,
            project_name="Sample Project",
            project_description="Migration planning fixture.",
            author="Example Maintainer",
        )
    )
    return root


def _registry(*rules: MigrationPathRule) -> MigrationRegistry:
    return MigrationRegistry(
        (
            MigrationContract(
                migration_id="python-engineering-v1-to-v2",
                source_baselines=(PYTHON_ENGINEERING_V1_BASELINE,),
                target_baseline="python-engineering-v2",
                profiles=("python-engineering",),
                rules=rules,
            ),
        )
    )


def _plan(root: Path, registry: MigrationRegistry):
    return plan_project_migration(
        ProjectMigrationRequest(
            project_root=root,
            migration_id="python-engineering-v1-to-v2",
        ),
        registry,
    )


def test_plans_safe_operations_deterministically_and_read_only(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    replace_path = root / "automation.txt"
    delete_path = root / "obsolete.txt"
    replace_path.write_bytes(b"source automation\n")
    delete_path.write_bytes(b"obsolete source\n")
    before = {
        replace_path: replace_path.read_bytes(),
        delete_path: delete_path.read_bytes(),
    }
    registry = _registry(
        MigrationPathRule(
            path="obsolete.txt",
            action=ACTION_DELETE_MACHINE_FILE,
            ownership=OWNERSHIP_MACHINE,
            source_content=b"obsolete source\n",
        ),
        MigrationPathRule(
            path="new-generated.txt",
            action=ACTION_CREATE_FILE,
            ownership=OWNERSHIP_GENERATED_ABSENT,
            target_content=b"generated target\n",
        ),
        MigrationPathRule(
            path="automation.txt",
            action=ACTION_REPLACE_MACHINE_FILE,
            ownership=OWNERSHIP_MACHINE,
            source_content=b"source automation\n",
            target_content=b"target automation\n",
        ),
    )

    first = _plan(root, registry)
    second = _plan(root, registry)

    assert first == second
    assert first.is_applicable is True
    assert first.manual_review == ()
    assert tuple(item.path for item in first.observations) == (
        "automation.txt",
        "new-generated.txt",
        "obsolete.txt",
    )
    assert tuple(item.state for item in first.observations) == (
        STATE_UNCHANGED_SOURCE,
        STATE_MISSING,
        STATE_UNCHANGED_SOURCE,
    )
    assert tuple(item.path for item in first.operations) == (
        "automation.txt",
        "new-generated.txt",
        "obsolete.txt",
    )
    assert first.operations[0].original_sha256 == hashlib.sha256(
        b"source automation\n"
    ).hexdigest()
    assert first.operations[1].original_sha256 is None
    assert first.operations[2].original_sha256 == hashlib.sha256(
        b"obsolete source\n"
    ).hexdigest()
    assert not (root / "new-generated.txt").exists()
    assert {path: path.read_bytes() for path in before} == before


def test_already_target_paths_produce_no_write_operations(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    (root / "automation.txt").write_bytes(b"target automation\n")
    (root / "new-generated.txt").write_bytes(b"generated target\n")
    registry = _registry(
        MigrationPathRule(
            path="automation.txt",
            action=ACTION_REPLACE_MACHINE_FILE,
            ownership=OWNERSHIP_MACHINE,
            source_content=b"source automation\n",
            target_content=b"target automation\n",
        ),
        MigrationPathRule(
            path="new-generated.txt",
            action=ACTION_CREATE_FILE,
            ownership=OWNERSHIP_GENERATED_ABSENT,
            target_content=b"generated target\n",
        ),
        MigrationPathRule(
            path="obsolete.txt",
            action=ACTION_DELETE_MACHINE_FILE,
            ownership=OWNERSHIP_MACHINE,
            source_content=b"obsolete source\n",
        ),
    )

    plan = _plan(root, registry)

    assert plan.operations == ()
    assert plan.manual_review == ()
    assert all(
        item.state == STATE_ALREADY_TARGET for item in plan.observations
    )


def test_locally_modified_machine_file_requires_manual_review(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    (root / "automation.txt").write_bytes(b"human local change\n")
    registry = _registry(
        MigrationPathRule(
            path="automation.txt",
            action=ACTION_REPLACE_MACHINE_FILE,
            ownership=OWNERSHIP_MACHINE,
            source_content=b"source automation\n",
            target_content=b"target automation\n",
        )
    )

    plan = _plan(root, registry)

    assert plan.is_applicable is False
    assert plan.operations == ()
    assert plan.observations[0].state == STATE_LOCALLY_MODIFIED
    assert plan.manual_review == ("automation.txt: locally_modified",)


def test_unexpected_create_target_requires_manual_review(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    (root / "new-generated.txt").write_bytes(b"unrecognized local file\n")
    registry = _registry(
        MigrationPathRule(
            path="new-generated.txt",
            action=ACTION_CREATE_FILE,
            ownership=OWNERSHIP_GENERATED_ABSENT,
            target_content=b"generated target\n",
        )
    )

    plan = _plan(root, registry)

    assert plan.operations == ()
    assert plan.observations[0].state == STATE_UNEXPECTED_PRESENT
    assert plan.manual_review == ("new-generated.txt: unexpected_present",)


def test_missing_required_replace_path_requires_manual_review(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    registry = _registry(
        MigrationPathRule(
            path="automation.txt",
            action=ACTION_REPLACE_MACHINE_FILE,
            ownership=OWNERSHIP_MACHINE,
            source_content=b"source automation\n",
            target_content=b"target automation\n",
        )
    )

    plan = _plan(root, registry)

    assert plan.operations == ()
    assert plan.observations[0].state == STATE_MISSING
    assert plan.manual_review == ("automation.txt: missing",)


@pytest.mark.parametrize("ownership", [OWNERSHIP_HUMAN, OWNERSHIP_UNKNOWN])
def test_non_machine_owned_replacement_is_never_automatic(
    tmp_path: Path,
    ownership: str,
) -> None:
    root = _bootstrap(tmp_path)
    (root / "preserved.txt").write_bytes(b"source\n")
    registry = _registry(
        MigrationPathRule(
            path="preserved.txt",
            action=ACTION_REPLACE_MACHINE_FILE,
            ownership=ownership,
            source_content=b"source\n",
            target_content=b"target\n",
        )
    )

    plan = _plan(root, registry)

    assert plan.operations == ()
    assert plan.observations[0].state == STATE_MANUAL_REVIEW
    assert plan.manual_review == ("preserved.txt: manual_review",)
    assert (root / "preserved.txt").read_bytes() == b"source\n"


def test_unsupported_file_type_requires_manual_review(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    (root / "automation.txt").mkdir()
    registry = _registry(
        MigrationPathRule(
            path="automation.txt",
            action=ACTION_REPLACE_MACHINE_FILE,
            ownership=OWNERSHIP_MACHINE,
            source_content=b"source\n",
            target_content=b"target\n",
        )
    )

    plan = _plan(root, registry)

    assert plan.operations == ()
    assert plan.observations[0].state == STATE_UNSUPPORTED_TYPE
    assert plan.manual_review == ("automation.txt: unsupported_type",)


def test_rule_path_traversal_is_rejected_before_planning() -> None:
    with pytest.raises(ValueError, match="bounded relative path"):
        MigrationPathRule(
            path="../outside.txt",
            action=ACTION_CREATE_FILE,
            ownership=OWNERSHIP_GENERATED_ABSENT,
            target_content=b"target\n",
        )


def test_symlink_escape_requires_manual_review(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"outside\n")
    link = root / "linked.txt"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink fixture unavailable: {exc}")
    registry = _registry(
        MigrationPathRule(
            path="linked.txt",
            action=ACTION_REPLACE_MACHINE_FILE,
            ownership=OWNERSHIP_MACHINE,
            source_content=b"outside\n",
            target_content=b"target\n",
        )
    )

    plan = _plan(root, registry)

    assert plan.operations == ()
    assert plan.observations[0].state == STATE_OUTSIDE_ROOT
    assert plan.manual_review == ("linked.txt: outside_root",)
    assert outside.read_bytes() == b"outside\n"


def test_duplicate_casefolded_rule_paths_are_rejected() -> None:
    first = MigrationPathRule(
        path="Generated.txt",
        action=ACTION_CREATE_FILE,
        ownership=OWNERSHIP_GENERATED_ABSENT,
        target_content=b"one\n",
    )
    second = MigrationPathRule(
        path="generated.txt",
        action=ACTION_CREATE_FILE,
        ownership=OWNERSHIP_GENERATED_ABSENT,
        target_content=b"two\n",
    )

    with pytest.raises(ValueError, match="rule paths must be unique"):
        MigrationContract(
            migration_id="duplicate-paths",
            source_baselines=(PYTHON_ENGINEERING_V1_BASELINE,),
            target_baseline="python-engineering-v2",
            profiles=("python-engineering",),
            rules=(first, second),
        )
