"""Deterministic documentation drift detection and planning for AUTO-0002."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .project_inspection import ProjectStateSnapshot

_WRITABLE_DOCUMENTS = (
    "CURRENT_STATUS.md",
    "MASTER_INDEX.md",
    "PROJECT_MAP.md",
)
_MARKER_NAMES = {
    "CURRENT_STATUS.md": "current-status",
    "MASTER_INDEX.md": "master-index",
    "PROJECT_MAP.md": "project-map",
}


class DocumentationSyncError(RuntimeError):
    """Raised when documentation synchronization cannot be planned safely."""


@dataclass(frozen=True)
class DocumentationDrift:
    document: str
    category: str
    expected: str
    observed: str


@dataclass(frozen=True)
class DocumentationDriftReport:
    project: ProjectStateSnapshot
    items: tuple[DocumentationDrift, ...]


@dataclass(frozen=True)
class DocumentationUpdate:
    document: str
    original_sha256: str
    replacement_content: str


@dataclass(frozen=True)
class DocumentationSyncPlan:
    project_root: Path
    updates: tuple[DocumentationUpdate, ...]


@dataclass(frozen=True)
class _OwnedSection:
    content: str
    body_start: int
    body_end: int
    body: str


def _markers(document: str) -> tuple[str, str]:
    marker_name = _MARKER_NAMES[document]
    return (
        f"<!-- ai-engineering:auto0002:{marker_name}:start -->",
        f"<!-- ai-engineering:auto0002:{marker_name}:end -->",
    )


def _read_document(root: Path, document: str) -> str:
    path = root / document
    try:
        return path.read_bytes().decode("utf-8")
    except FileNotFoundError as error:
        raise DocumentationSyncError(f"Required document missing: {document}") from error
    except (OSError, UnicodeDecodeError) as error:
        raise DocumentationSyncError(f"Document could not be read: {document}") from error


def _owned_section(content: str, document: str) -> _OwnedSection | None:
    start_marker, end_marker = _markers(document)
    start = content.find(start_marker)
    end = content.find(end_marker)
    if start < 0 or end < 0:
        return None
    if content.find(start_marker, start + 1) >= 0:
        return None
    if content.find(end_marker, end + 1) >= 0:
        return None
    if end <= start:
        return None

    body_start = start + len(start_marker)
    body_end = end
    return _OwnedSection(
        content=content,
        body_start=body_start,
        body_end=body_end,
        body=content[body_start:body_end],
    )


def _line_ending(content: str) -> str:
    return "\r\n" if "\r\n" in content else "\n"


def _render_project_map(snapshot: ProjectStateSnapshot, newline: str) -> str:
    lines = ["", "### Managed Repository Paths", ""]
    for entry in snapshot.files:
        lines.append(f"- `{entry.relative_path}` ({entry.kind})")
    return newline.join(lines) + newline


def _root_markdown_files(snapshot: ProjectStateSnapshot) -> tuple[str, ...]:
    return tuple(
        sorted(
            entry.relative_path
            for entry in snapshot.files
            if entry.kind == "file"
            and "/" not in entry.relative_path
            and entry.relative_path.endswith(".md")
        )
    )


def _render_master_index(snapshot: ProjectStateSnapshot, newline: str) -> str:
    lines = ["", "### Managed Document Index", ""]
    for document in _root_markdown_files(snapshot):
        lines.append(f"- `{document}` — observed")
    return newline.join(lines) + newline


def _status_values(snapshot: ProjectStateSnapshot) -> tuple[tuple[str, str], ...]:
    return (
        ("project_name", snapshot.project_name or "unknown"),
        ("package_name", snapshot.package_name or "unknown"),
        ("git_repository", "yes" if snapshot.git_repository else "no"),
        ("git_branch", snapshot.git_branch or "none"),
        ("git_head", snapshot.git_head or "none"),
    )


def _render_current_status(snapshot: ProjectStateSnapshot, newline: str) -> str:
    lines = ["", "### Managed Local Facts", ""]
    lines.extend(f"- `{key}`: `{value}`" for key, value in _status_values(snapshot))
    return newline.join(lines) + newline


def _expected_body(
    snapshot: ProjectStateSnapshot,
    document: str,
    content: str,
) -> str:
    newline = _line_ending(content)
    if document == "PROJECT_MAP.md":
        return _render_project_map(snapshot, newline)
    if document == "MASTER_INDEX.md":
        return _render_master_index(snapshot, newline)
    return _render_current_status(snapshot, newline)


def _path_set_from_body(body: str) -> set[str]:
    paths: set[str] = set()
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- `"):
            continue
        end = stripped.find("`", 3)
        if end > 3:
            paths.add(stripped[3:end])
    return paths


def _map_drift(
    snapshot: ProjectStateSnapshot,
    observed_body: str,
) -> list[DocumentationDrift]:
    expected = {entry.relative_path for entry in snapshot.files}
    observed = _path_set_from_body(observed_body)
    items: list[DocumentationDrift] = []
    for path in sorted(expected - observed):
        items.append(
            DocumentationDrift(
                "PROJECT_MAP.md",
                "missing_repository_path",
                path,
                "missing",
            )
        )
    for path in sorted(observed - expected):
        items.append(
            DocumentationDrift(
                "PROJECT_MAP.md",
                "stale_repository_path",
                "absent",
                path,
            )
        )
    return items


def _index_drift(
    snapshot: ProjectStateSnapshot,
    observed_body: str,
) -> list[DocumentationDrift]:
    expected = set(_root_markdown_files(snapshot))
    observed = _path_set_from_body(observed_body)
    items: list[DocumentationDrift] = []
    for document in sorted(expected - observed):
        items.append(
            DocumentationDrift(
                "MASTER_INDEX.md",
                "missing_indexed_document",
                document,
                "missing",
            )
        )
    for document in sorted(observed - expected):
        items.append(
            DocumentationDrift(
                "MASTER_INDEX.md",
                "stale_indexed_document",
                "absent",
                document,
            )
        )
    return items


def _status_drift(
    snapshot: ProjectStateSnapshot,
    observed_body: str,
) -> list[DocumentationDrift]:
    items: list[DocumentationDrift] = []
    for key, value in _status_values(snapshot):
        expected_line = f"- `{key}`: `{value}`"
        if expected_line not in observed_body.splitlines():
            items.append(
                DocumentationDrift(
                    "CURRENT_STATUS.md",
                    "stale_bounded_status_fact",
                    expected_line,
                    "missing_or_stale",
                )
            )
    return items


def detect_documentation_drift(
    snapshot: ProjectStateSnapshot,
) -> DocumentationDriftReport:
    """Return deterministic drift for the three approved AUTO-0002 documents."""

    items: list[DocumentationDrift] = []
    for document in _WRITABLE_DOCUMENTS:
        content = _read_document(snapshot.project_root, document)
        section = _owned_section(content, document)
        if section is None:
            items.append(
                DocumentationDrift(
                    document,
                    "manual_review_required",
                    "valid AUTO-0002 ownership markers",
                    "missing_or_malformed_markers",
                )
            )
            continue

        if document == "PROJECT_MAP.md":
            items.extend(_map_drift(snapshot, section.body))
        elif document == "MASTER_INDEX.md":
            items.extend(_index_drift(snapshot, section.body))
        else:
            items.extend(_status_drift(snapshot, section.body))

        expected = _expected_body(snapshot, document, content)
        if section.body != expected and not any(
            item.document == document for item in items
        ):
            items.append(
                DocumentationDrift(
                    document,
                    "deterministic_format_drift",
                    expected,
                    section.body,
                )
            )

    return DocumentationDriftReport(project=snapshot, items=tuple(items))


def _replace_owned_body(section: _OwnedSection, replacement_body: str) -> str:
    return (
        section.content[: section.body_start]
        + replacement_body
        + section.content[section.body_end :]
    )


def plan_documentation_sync(
    report: DocumentationDriftReport,
) -> DocumentationSyncPlan:
    """Build a deterministic, read-only synchronization plan from a drift report."""

    manual_review_documents = {
        item.document
        for item in report.items
        if item.category == "manual_review_required"
    }
    drift_documents = {
        item.document
        for item in report.items
        if item.category != "manual_review_required"
    }

    updates: list[DocumentationUpdate] = []
    for document in _WRITABLE_DOCUMENTS:
        if document not in drift_documents or document in manual_review_documents:
            continue
        content = _read_document(report.project.project_root, document)
        section = _owned_section(content, document)
        if section is None:
            raise DocumentationSyncError(
                f"Ownership markers became invalid while planning: {document}"
            )
        replacement_body = _expected_body(report.project, document, content)
        replacement_content = _replace_owned_body(section, replacement_body)
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        updates.append(
            DocumentationUpdate(
                document=document,
                original_sha256=digest,
                replacement_content=replacement_content,
            )
        )

    return DocumentationSyncPlan(
        project_root=report.project.project_root,
        updates=tuple(updates),
    )
