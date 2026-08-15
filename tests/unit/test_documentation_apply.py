from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from ai_engineering.documentation_apply import apply_documentation_sync
from ai_engineering.documentation_sync import (
    DocumentationSyncError,
    DocumentationSyncPlan,
    DocumentationUpdate,
    detect_documentation_drift,
    plan_documentation_sync,
)
from ai_engineering.project_inspection import (
    ProjectInspectionRequest,
    inspect_project_state,
)


def _document(mark: str, body: str, human: str = "Human content") -> str:
    return (
        f"# Document\n\n{human}\n\n"
        f"<!-- ai-engineering:auto0002:{mark}:start -->"
        f"{body}"
        f"<!-- ai-engineering:auto0002:{mark}:end -->\n"
        "\nHuman tail\n"
    )


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / "src" / "sample_pkg").mkdir(parents=True)
    (root / "src" / "sample_pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / "README.md").write_text("# Sample\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nname = "sample-project"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (root / "CURRENT_STATUS.md").write_text(
        _document("current-status", "\n- stale: value\n"),
        encoding="utf-8",
    )
    (root / "PROJECT_MAP.md").write_text(
        _document("project-map", "\n- `gone.txt` (file)\n"),
        encoding="utf-8",
    )
    (root / "MASTER_INDEX.md").write_text(
        _document("master-index", "\n- `OLD.md` — observed\n"),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Apply Test",
            "-c",
            "user.email=apply@example.invalid",
            "commit",
            "-m",
            "initial",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return root


def _plan(root: Path) -> DocumentationSyncPlan:
    snapshot = inspect_project_state(ProjectInspectionRequest(root))
    return plan_documentation_sync(detect_documentation_drift(snapshot))


def test_apply_writes_only_planned_documents_and_clears_drift(tmp_path: Path) -> None:
    root = _project(tmp_path)
    readme_before = (root / "README.md").read_bytes()
    result = apply_documentation_sync(_plan(root))

    assert result.project_root == root.resolve()
    assert result.changed_documents == (
        "CURRENT_STATUS.md",
        "MASTER_INDEX.md",
        "PROJECT_MAP.md",
    )
    assert (root / "README.md").read_bytes() == readme_before
    refreshed = inspect_project_state(ProjectInspectionRequest(root))
    assert detect_documentation_drift(refreshed).items == ()


def test_apply_preserves_human_owned_content(tmp_path: Path) -> None:
    root = _project(tmp_path)
    path = root / "PROJECT_MAP.md"
    before = path.read_text(encoding="utf-8")

    apply_documentation_sync(_plan(root))
    after = path.read_text(encoding="utf-8")

    assert after.startswith("# Document\n\nHuman content\n\n")
    assert after.endswith("\nHuman tail\n")
    assert before.split("<!-- ai-engineering:auto0002:project-map:start -->")[0] == (
        after.split("<!-- ai-engineering:auto0002:project-map:start -->")[0]
    )


def test_stale_plan_fails_before_any_write(tmp_path: Path) -> None:
    root = _project(tmp_path)
    plan = _plan(root)
    originals = {
        update.document: (root / update.document).read_bytes()
        for update in plan.updates
    }
    stale = root / "MASTER_INDEX.md"
    stale.write_text(
        stale.read_text(encoding="utf-8") + "changed\n",
        encoding="utf-8",
    )

    with pytest.raises(DocumentationSyncError, match="Stale synchronization plan"):
        apply_documentation_sync(plan)

    assert (root / "CURRENT_STATUS.md").read_bytes() == originals["CURRENT_STATUS.md"]
    assert (root / "PROJECT_MAP.md").read_bytes() == originals["PROJECT_MAP.md"]


def test_apply_rejects_unapproved_document(tmp_path: Path) -> None:
    root = _project(tmp_path)
    readme = root / "README.md"
    original = readme.read_bytes()
    plan = DocumentationSyncPlan(
        project_root=root.resolve(),
        updates=(
            DocumentationUpdate(
                document="README.md",
                original_sha256=hashlib.sha256(original).hexdigest(),
                replacement_content="# Changed\n",
            ),
        ),
    )

    with pytest.raises(DocumentationSyncError, match="unsupported document"):
        apply_documentation_sync(plan)
    assert readme.read_bytes() == original


def test_apply_rejects_duplicate_documents(tmp_path: Path) -> None:
    root = _project(tmp_path)
    update = _plan(root).updates[0]
    plan = DocumentationSyncPlan(root.resolve(), (update, update))

    with pytest.raises(DocumentationSyncError, match="duplicate documents"):
        apply_documentation_sync(plan)


def test_apply_rejects_plan_that_changes_human_prefix(tmp_path: Path) -> None:
    root = _project(tmp_path)
    plan = _plan(root)
    original = plan.updates[0]
    forged = DocumentationUpdate(
        document=original.document,
        original_sha256=original.original_sha256,
        replacement_content=original.replacement_content.replace(
            "# Document",
            "# Rewritten Human Heading",
            1,
        ),
    )
    forged_plan = DocumentationSyncPlan(root.resolve(), (forged,))

    with pytest.raises(DocumentationSyncError, match="Human-owned prefix changed"):
        apply_documentation_sync(forged_plan)


def test_empty_plan_is_successful_and_read_only(tmp_path: Path) -> None:
    root = _project(tmp_path)
    before = {path: path.read_bytes() for path in root.glob("*.md")}
    result = apply_documentation_sync(DocumentationSyncPlan(root.resolve(), ()))

    assert result.changed_documents == ()
    assert {path: path.read_bytes() for path in root.glob("*.md")} == before
