from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from ai_engineering.documentation_sync import (
    detect_documentation_drift,
    plan_documentation_sync,
)
from ai_engineering.project_inspection import (
    ProjectInspectionRequest,
    ProjectStateSnapshot,
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


def _write_managed_documents(root: Path) -> None:
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


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / "src" / "sample_pkg").mkdir(parents=True)
    (root / "src" / "sample_pkg" / "__init__.py").write_text(
        "",
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Sample\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nname = "sample-project"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    _write_managed_documents(root)
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Sync Test",
            "-c",
            "user.email=sync@example.invalid",
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


def _snapshot(root: Path) -> ProjectStateSnapshot:
    return inspect_project_state(ProjectInspectionRequest(root))


def test_detects_project_map_missing_and_stale_paths(tmp_path: Path) -> None:
    report = detect_documentation_drift(_snapshot(_project(tmp_path)))
    categories = {(item.document, item.category) for item in report.items}

    assert ("PROJECT_MAP.md", "missing_repository_path") in categories
    assert ("PROJECT_MAP.md", "stale_repository_path") in categories


def test_detects_master_index_missing_and_stale_documents(tmp_path: Path) -> None:
    report = detect_documentation_drift(_snapshot(_project(tmp_path)))
    categories = {(item.document, item.category) for item in report.items}

    assert ("MASTER_INDEX.md", "missing_indexed_document") in categories
    assert ("MASTER_INDEX.md", "stale_indexed_document") in categories


def test_detects_only_bounded_current_status_facts(tmp_path: Path) -> None:
    report = detect_documentation_drift(_snapshot(_project(tmp_path)))
    status_items = [
        item for item in report.items if item.document == "CURRENT_STATUS.md"
    ]

    assert status_items
    assert {item.category for item in status_items} == {
        "stale_bounded_status_fact"
    }
    assert any("git_branch" in item.expected for item in status_items)
    assert not any("release" in item.expected.lower() for item in status_items)


def test_missing_markers_require_manual_review_and_are_not_planned(
    tmp_path: Path,
) -> None:
    root = _project(tmp_path)
    original = "# Human-only status\nDo not rewrite me.\n"
    (root / "CURRENT_STATUS.md").write_text(original, encoding="utf-8")

    report = detect_documentation_drift(_snapshot(root))
    plan = plan_documentation_sync(report)

    assert any(
        item.document == "CURRENT_STATUS.md"
        and item.category == "manual_review_required"
        for item in report.items
    )
    assert "CURRENT_STATUS.md" not in {update.document for update in plan.updates}
    assert (root / "CURRENT_STATUS.md").read_text(encoding="utf-8") == original


def test_malformed_duplicate_markers_require_manual_review(tmp_path: Path) -> None:
    root = _project(tmp_path)
    duplicate = (
        "<!-- ai-engineering:auto0002:project-map:start -->\n"
        "<!-- ai-engineering:auto0002:project-map:start -->\n"
        "x\n"
        "<!-- ai-engineering:auto0002:project-map:end -->\n"
    )
    (root / "PROJECT_MAP.md").write_text(duplicate, encoding="utf-8")

    report = detect_documentation_drift(_snapshot(root))

    assert any(
        item.document == "PROJECT_MAP.md"
        and item.category == "manual_review_required"
        for item in report.items
    )


def test_planning_is_read_only_stable_and_contains_original_digest(
    tmp_path: Path,
) -> None:
    root = _project(tmp_path)
    before = {
        name: (root / name).read_bytes()
        for name in ("CURRENT_STATUS.md", "PROJECT_MAP.md", "MASTER_INDEX.md")
    }
    report = detect_documentation_drift(_snapshot(root))

    first = plan_documentation_sync(report)
    second = plan_documentation_sync(report)

    assert first == second
    assert len(first.updates) == 3
    for update in first.updates:
        expected_digest = hashlib.sha256(before[update.document]).hexdigest()
        assert update.original_sha256 == expected_digest
        assert (root / update.document).read_bytes() == before[update.document]


def test_plan_preserves_human_content_outside_owned_section(tmp_path: Path) -> None:
    root = _project(tmp_path)
    report = detect_documentation_drift(_snapshot(root))
    plan = plan_documentation_sync(report)

    update = next(
        item for item in plan.updates if item.document == "PROJECT_MAP.md"
    )
    normalized = update.replacement_content.replace("\r\n", "\n")
    assert normalized.startswith("# Document\n\nHuman content\n\n")
    assert normalized.endswith("\nHuman tail\n")
    assert "gone.txt" not in update.replacement_content
    assert "src/sample_pkg/__init__.py" in update.replacement_content
    assert str(root.resolve()) not in update.replacement_content
    assert "\\" not in update.replacement_content


def test_plan_uses_neutral_master_index_status(tmp_path: Path) -> None:
    root = _project(tmp_path)
    plan = plan_documentation_sync(
        detect_documentation_drift(_snapshot(root))
    )
    update = next(
        item for item in plan.updates if item.document == "MASTER_INDEX.md"
    )

    assert "`README.md` — observed" in update.replacement_content
    assert "complete" not in update.replacement_content.lower()
    assert "verified" not in update.replacement_content.lower()


def test_planned_replacements_clear_drift_when_caller_applies_them(
    tmp_path: Path,
) -> None:
    root = _project(tmp_path)
    snapshot = _snapshot(root)
    plan = plan_documentation_sync(detect_documentation_drift(snapshot))

    for update in plan.updates:
        (root / update.document).write_bytes(
            update.replacement_content.encode("utf-8")
        )

    refreshed = _snapshot(root)
    assert detect_documentation_drift(refreshed).items == ()


def test_crlf_human_content_is_preserved_in_planned_replacement(
    tmp_path: Path,
) -> None:
    root = _project(tmp_path)
    path = root / "CURRENT_STATUS.md"
    content = _document("current-status", "\n- stale: value\n").replace(
        "\n",
        "\r\n",
    )
    path.write_bytes(content.encode("utf-8"))

    plan = plan_documentation_sync(detect_documentation_drift(_snapshot(root)))
    update = next(
        item for item in plan.updates if item.document == "CURRENT_STATUS.md"
    )

    assert update.replacement_content.startswith(
        "# Document\r\n\r\nHuman content\r\n\r\n"
    )
    assert update.replacement_content.endswith("\r\nHuman tail\r\n")
