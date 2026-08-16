from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering.engineering_bootstrap import (
    EngineeringBootstrapRequest,
    bootstrap_engineering_project,
)
from ai_engineering.project_migration import (
    DEFAULT_MIGRATION_REGISTRY,
    PYTHON_ENGINEERING_V1_BASELINE,
    MigrationContract,
    MigrationRegistry,
    UnsupportedMigrationError,
    UnsupportedProjectIdentityError,
    detect_project_identity,
)


def _bootstrap(tmp_path: Path) -> Path:
    target = tmp_path / "sample-project"
    bootstrap_engineering_project(
        EngineeringBootstrapRequest(
            target_directory=target,
            project_name="Sample Project",
            project_description="Migration identity fixture.",
            author="Example Maintainer",
        )
    )
    return target


def test_detects_approved_python_engineering_v1_identity(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)

    identity = detect_project_identity(root)

    assert identity.project_root == root.resolve()
    assert identity.profile == "python-engineering"
    assert identity.baseline == PYTHON_ENGINEERING_V1_BASELINE
    assert identity.distribution_name == "sample-project"
    assert identity.package_name == "sample_project"
    assert identity.project_version == "0.1.0"
    assert dict(identity.evidence_sha256)["pyproject.toml"]
    assert dict(identity.evidence_sha256)["tests/test_smoke.py"]


def test_identity_detection_is_read_only(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    observed_paths = (
        root / "pyproject.toml",
        root / ".gitignore",
        root / "README.md",
        root / "src" / "sample_project" / "__init__.py",
        root / "tests" / "test_smoke.py",
    )
    before = {path: path.read_bytes() for path in observed_paths}

    detect_project_identity(root)

    after = {path: path.read_bytes() for path in observed_paths}
    assert after == before


def test_human_document_changes_do_not_destroy_identity(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\nHuman-owned extension.\n",
        encoding="utf-8",
    )

    identity = detect_project_identity(root)

    assert identity.baseline == PYTHON_ENGINEERING_V1_BASELINE
    assert dict(identity.evidence_sha256)["README.md"]


def test_arbitrary_repository_fails_closed(tmp_path: Path) -> None:
    root = tmp_path / "arbitrary"
    root.mkdir()
    (root / "pyproject.toml").write_text(
        '[project]\nname = "arbitrary"\nversion = "1.0.0"\n',
        encoding="utf-8",
    )

    with pytest.raises(UnsupportedProjectIdentityError):
        detect_project_identity(root)


def test_modified_machine_owned_scaffold_fails_closed(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    package_init = root / "src" / "sample_project" / "__init__.py"
    package_init.write_text("# local modification\n", encoding="utf-8")

    with pytest.raises(
        UnsupportedProjectIdentityError,
        match="differs from python-engineering V1",
    ):
        detect_project_identity(root)


def test_missing_required_document_fails_closed(tmp_path: Path) -> None:
    root = _bootstrap(tmp_path)
    (root / "PROJECT_CONTEXT.md").unlink()

    with pytest.raises(
        UnsupportedProjectIdentityError,
        match="Required identity path is unavailable",
    ):
        detect_project_identity(root)


def test_registry_is_deterministic_and_resolves_exact_edge(tmp_path: Path) -> None:
    identity = detect_project_identity(_bootstrap(tmp_path))
    later = MigrationContract(
        migration_id="migration-b",
        source_baselines=(PYTHON_ENGINEERING_V1_BASELINE,),
        target_baseline="python-engineering-v3",
        profiles=("python-engineering",),
    )
    first = MigrationContract(
        migration_id="migration-a",
        source_baselines=(PYTHON_ENGINEERING_V1_BASELINE,),
        target_baseline="python-engineering-v2",
        profiles=("python-engineering",),
    )
    registry = MigrationRegistry((later, first))

    assert tuple(item.migration_id for item in registry.contracts) == (
        "migration-a",
        "migration-b",
    )
    assert registry.resolve("migration-a", identity) == first


def test_registry_rejects_duplicate_ids() -> None:
    first = MigrationContract(
        migration_id="same-id",
        source_baselines=("baseline-a",),
        target_baseline="baseline-b",
        profiles=("python-engineering",),
    )
    second = MigrationContract(
        migration_id="same-id",
        source_baselines=("baseline-b",),
        target_baseline="baseline-c",
        profiles=("python-engineering",),
    )

    with pytest.raises(ValueError, match="migration ids must be unique"):
        MigrationRegistry((first, second))


def test_registry_rejects_wrong_profile_or_source(tmp_path: Path) -> None:
    identity = detect_project_identity(_bootstrap(tmp_path))
    wrong_profile = MigrationRegistry(
        (
            MigrationContract(
                migration_id="wrong-profile",
                source_baselines=(PYTHON_ENGINEERING_V1_BASELINE,),
                target_baseline="target",
                profiles=("other-profile",),
            ),
        )
    )
    wrong_source = MigrationRegistry(
        (
            MigrationContract(
                migration_id="wrong-source",
                source_baselines=("other-baseline",),
                target_baseline="target",
                profiles=("python-engineering",),
            ),
        )
    )

    with pytest.raises(UnsupportedMigrationError, match="does not support profile"):
        wrong_profile.resolve("wrong-profile", identity)
    with pytest.raises(
        UnsupportedMigrationError,
        match="does not support source baseline",
    ):
        wrong_source.resolve("wrong-source", identity)


def test_default_registry_has_no_unapproved_migrations(tmp_path: Path) -> None:
    identity = detect_project_identity(_bootstrap(tmp_path))

    assert DEFAULT_MIGRATION_REGISTRY.contracts == ()
    with pytest.raises(UnsupportedMigrationError, match="Unsupported migration id"):
        DEFAULT_MIGRATION_REGISTRY.resolve("upgrade-to-latest", identity)
