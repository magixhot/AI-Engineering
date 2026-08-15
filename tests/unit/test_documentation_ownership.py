from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest

import ai_engineering.documentation_ownership as ownership_module
from ai_engineering.documentation_ownership import (
    DocumentationOwnershipError,
    apply_documentation_ownership_initialization,
    classify_document_ownership,
    plan_documentation_ownership_initialization,
)
from ai_engineering.documentation_sync import detect_documentation_drift
from ai_engineering.project_inspection import (
    ProjectInspectionRequest,
    ProjectStateSnapshot,
    inspect_project_state,
)


def _snapshot(root: Path) -> ProjectStateSnapshot:
    return ProjectStateSnapshot(
        project_root=root,
        project_name="sample",
        package_name="sample_pkg",
        git_repository=False,
        git_branch=None,
        git_head=None,
        files=(),
    )


def _write_targets(root: Path, newline: str = "\n") -> dict[str, bytes]:
    originals: dict[str, bytes] = {}
    for name in ("CURRENT_STATUS.md", "MASTER_INDEX.md", "PROJECT_MAP.md"):
        content = f"# {name}{newline}{newline}Human content{newline}"
        raw = content.encode("utf-8")
        (root / name).write_bytes(raw)
        originals[name] = raw
    return originals


def _apply_project(tmp_path: Path) -> tuple[Path, dict[str, bytes]]:
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
    originals = _write_targets(root)
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Ownership Test",
            "-c",
            "user.email=ownership@example.invalid",
            "commit",
            "-m",
            "initial",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return root, originals


def _inspected_snapshot(root: Path) -> ProjectStateSnapshot:
    return inspect_project_state(ProjectInspectionRequest(root))


def test_classifies_required_marker_states() -> None:
    start = "<!-- ai-engineering:auto0002:project-map:start -->"
    end = "<!-- ai-engineering:auto0002:project-map:end -->"

    assert (
        classify_document_ownership("PROJECT_MAP.md", "human\n").state
        == "missing"
    )
    assert classify_document_ownership("PROJECT_MAP.md", start).state == "partial"
    assert (
        classify_document_ownership(
            "PROJECT_MAP.md",
            start + start + end,
        ).state
        == "duplicate"
    )
    assert (
        classify_document_ownership(
            "PROJECT_MAP.md",
            end + start,
        ).state
        == "malformed"
    )
    assert (
        classify_document_ownership(
            "PROJECT_MAP.md",
            start + end,
        ).state
        == "initialized"
    )


def test_marker_like_unknown_content_is_unsupported() -> None:
    result = classify_document_ownership(
        "PROJECT_MAP.md",
        "<!-- ai-engineering:auto0002:legacy:start -->\n",
    )
    assert result.state == "unsupported"


def test_mixed_newlines_are_unsupported() -> None:
    result = classify_document_ownership(
        "CURRENT_STATUS.md",
        "# Status\r\nHuman\n",
    )
    assert result.state == "unsupported"


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_plan_is_read_only_deterministic_and_preserves_original_prefix(
    tmp_path: Path,
    newline: str,
) -> None:
    originals = _write_targets(tmp_path, newline)
    snapshot = _snapshot(tmp_path)

    first = plan_documentation_ownership_initialization(snapshot)
    second = plan_documentation_ownership_initialization(snapshot)

    assert first == second
    assert first.manual_review == ()
    assert len(first.updates) == 3
    for update in first.updates:
        original = originals[update.document]
        assert (tmp_path / update.document).read_bytes() == original
        assert update.replacement_content.encode("utf-8").startswith(original)
        assert update.original_sha256 == hashlib.sha256(original).hexdigest()
        assert update.replacement_content.count("ai-engineering:auto0002:") == 2
        if newline == "\r\n":
            assert "\n" not in update.replacement_content.replace("\r\n", "")


def test_initialized_document_is_noop(tmp_path: Path) -> None:
    _write_targets(tmp_path)
    path = tmp_path / "PROJECT_MAP.md"
    path.write_text(
        "# Map\n\n<!-- ai-engineering:auto0002:project-map:start -->\n"
        "### Managed Repository Paths\n"
        "<!-- ai-engineering:auto0002:project-map:end -->\n",
        encoding="utf-8",
    )

    plan = plan_documentation_ownership_initialization(
        _snapshot(tmp_path), ("PROJECT_MAP.md",)
    )

    assert plan.updates == ()
    assert plan.manual_review == ()
    assert plan.classifications[0].state == "initialized"


def test_partial_duplicate_and_missing_document_require_manual_review(
    tmp_path: Path,
) -> None:
    _write_targets(tmp_path)
    (tmp_path / "CURRENT_STATUS.md").write_text(
        "<!-- ai-engineering:auto0002:current-status:start -->\n",
        encoding="utf-8",
    )
    (tmp_path / "MASTER_INDEX.md").write_text(
        "<!-- ai-engineering:auto0002:master-index:start -->\n"
        "<!-- ai-engineering:auto0002:master-index:start -->\n"
        "<!-- ai-engineering:auto0002:master-index:end -->\n",
        encoding="utf-8",
    )
    (tmp_path / "PROJECT_MAP.md").unlink()

    plan = plan_documentation_ownership_initialization(_snapshot(tmp_path))

    assert plan.updates == ()
    assert plan.manual_review == (
        "CURRENT_STATUS.md",
        "MASTER_INDEX.md",
        "PROJECT_MAP.md",
    )
    assert tuple(item.state for item in plan.classifications) == (
        "partial",
        "duplicate",
        "missing_document",
    )


def test_rejects_document_outside_v1_scope(tmp_path: Path) -> None:
    with pytest.raises(DocumentationOwnershipError, match="Unsupported document"):
        plan_documentation_ownership_initialization(
            _snapshot(tmp_path), ("README.md",)
        )


def test_rejects_duplicate_document_selection(tmp_path: Path) -> None:
    with pytest.raises(DocumentationOwnershipError, match="Duplicate document"):
        plan_documentation_ownership_initialization(
            _snapshot(tmp_path), ("PROJECT_MAP.md", "PROJECT_MAP.md")
        )


def test_apply_initializes_all_documents_and_hands_off_to_auto0002(
    tmp_path: Path,
) -> None:
    root, _ = _apply_project(tmp_path)
    snapshot = _inspected_snapshot(root)
    plan = plan_documentation_ownership_initialization(snapshot)

    result = apply_documentation_ownership_initialization(plan)

    assert result.changed_documents == (
        "CURRENT_STATUS.md",
        "MASTER_INDEX.md",
        "PROJECT_MAP.md",
    )
    refreshed = _inspected_snapshot(root)
    assert detect_documentation_drift(refreshed).items == ()
    follow_up = plan_documentation_ownership_initialization(refreshed)
    assert follow_up.updates == ()
    assert follow_up.manual_review == ()
    assert all(
        item.state == "initialized" for item in follow_up.classifications
    )


def test_apply_rejects_stale_plan_before_any_write(tmp_path: Path) -> None:
    root, originals = _apply_project(tmp_path)
    plan = plan_documentation_ownership_initialization(_inspected_snapshot(root))
    path = root / "MASTER_INDEX.md"
    path.write_text("changed after plan\n", encoding="utf-8")
    changed = path.read_bytes()

    with pytest.raises(DocumentationOwnershipError, match="Stale initialization"):
        apply_documentation_ownership_initialization(plan)

    assert (root / "CURRENT_STATUS.md").read_bytes() == originals[
        "CURRENT_STATUS.md"
    ]
    assert (root / "MASTER_INDEX.md").read_bytes() == changed
    assert (root / "PROJECT_MAP.md").read_bytes() == originals["PROJECT_MAP.md"]


def test_manual_review_prevents_all_writes(tmp_path: Path) -> None:
    root, _ = _apply_project(tmp_path)
    path = root / "CURRENT_STATUS.md"
    path.write_text(
        "<!-- ai-engineering:auto0002:current-status:start -->\n",
        encoding="utf-8",
    )
    before = {
        name: (root / name).read_bytes()
        for name in ("CURRENT_STATUS.md", "MASTER_INDEX.md", "PROJECT_MAP.md")
    }
    plan = plan_documentation_ownership_initialization(_inspected_snapshot(root))
    assert plan.manual_review == ("CURRENT_STATUS.md",)
    assert len(plan.updates) == 2

    with pytest.raises(DocumentationOwnershipError, match="manual review"):
        apply_documentation_ownership_initialization(plan)

    for name, content in before.items():
        assert (root / name).read_bytes() == content


def test_replace_failure_rolls_back_previous_document(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, originals = _apply_project(tmp_path)
    plan = plan_documentation_ownership_initialization(_inspected_snapshot(root))
    real_replace = os.replace
    replacement_calls = 0
    failed_once = False

    def failing_replace(source: str | Path, destination: str | Path) -> None:
        nonlocal replacement_calls, failed_once
        source_path = Path(source)
        if source_path.name.endswith(".auto0003.tmp") and not failed_once:
            replacement_calls += 1
            if replacement_calls == 2:
                failed_once = True
                raise OSError("simulated replace failure")
        real_replace(source, destination)

    monkeypatch.setattr(ownership_module.os, "replace", failing_replace)

    with pytest.raises(DocumentationOwnershipError, match="apply failed"):
        apply_documentation_ownership_initialization(plan)

    for name, content in originals.items():
        assert (root / name).read_bytes() == content


def test_apply_does_not_change_git_head_or_index(tmp_path: Path) -> None:
    root, _ = _apply_project(tmp_path)
    plan = plan_documentation_ownership_initialization(_inspected_snapshot(root))
    head_before = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
    ).strip()
    index_before = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"],
        cwd=root,
        text=True,
    )

    apply_documentation_ownership_initialization(plan)

    head_after = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
    ).strip()
    index_after = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"],
        cwd=root,
        text=True,
    )
    assert head_after == head_before
    assert index_after == index_before == ""
