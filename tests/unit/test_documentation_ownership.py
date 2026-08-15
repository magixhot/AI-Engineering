from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ai_engineering.documentation_ownership import (
    DocumentationOwnershipError,
    classify_document_ownership,
    plan_documentation_ownership_initialization,
)
from ai_engineering.project_inspection import ProjectStateSnapshot


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


def test_classifies_required_marker_states() -> None:
    start = "<!-- ai-engineering:auto0002:project-map:start -->"
    end = "<!-- ai-engineering:auto0002:project-map:end -->"

    assert classify_document_ownership("PROJECT_MAP.md", "human\n").state == "missing"
    assert classify_document_ownership("PROJECT_MAP.md", start).state == "partial"
    duplicate = classify_document_ownership(
        "PROJECT_MAP.md",
        start + start + end,
    )
    malformed = classify_document_ownership(
        "PROJECT_MAP.md",
        end + start,
    )
    initialized = classify_document_ownership(
        "PROJECT_MAP.md",
        start + end,
    )
    assert duplicate.state == "duplicate"
    assert malformed.state == "malformed"
    assert initialized.state == "initialized"


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
