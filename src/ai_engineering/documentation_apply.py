"""Guarded apply and verification for AUTO-0002 documentation plans."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .documentation_sync import (
    DocumentationSyncError,
    DocumentationSyncPlan,
    detect_documentation_drift,
)
from .project_inspection import ProjectInspectionRequest, inspect_project_state

_APPROVED_DOCUMENTS = {
    "CURRENT_STATUS.md",
    "MASTER_INDEX.md",
    "PROJECT_MAP.md",
}
_MARKER_NAMES = {
    "CURRENT_STATUS.md": "current-status",
    "MASTER_INDEX.md": "master-index",
    "PROJECT_MAP.md": "project-map",
}


@dataclass(frozen=True)
class DocumentationSyncResult:
    project_root: Path
    changed_documents: tuple[str, ...]


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _marker_bounds(content: str, document: str) -> tuple[int, int] | None:
    marker = _MARKER_NAMES[document]
    start_marker = f"<!-- ai-engineering:auto0002:{marker}:start -->"
    end_marker = f"<!-- ai-engineering:auto0002:{marker}:end -->"
    start = content.find(start_marker)
    end = content.find(end_marker)
    if start < 0 or end < 0 or end <= start:
        return None
    if content.find(start_marker, start + 1) >= 0:
        return None
    if content.find(end_marker, end + 1) >= 0:
        return None
    return start + len(start_marker), end


def _validate_plan(plan: DocumentationSyncPlan) -> None:
    documents = [update.document for update in plan.updates]
    if len(documents) != len(set(documents)):
        raise DocumentationSyncError("Synchronization plan contains duplicate documents")
    unsupported = sorted(set(documents) - _APPROVED_DOCUMENTS)
    if unsupported:
        raise DocumentationSyncError(
            f"Synchronization plan contains unsupported document: {unsupported[0]}"
        )


def _preflight(plan: DocumentationSyncPlan) -> dict[str, bytes]:
    originals: dict[str, bytes] = {}
    for update in plan.updates:
        path = plan.project_root / update.document
        try:
            current = path.read_bytes()
            current_text = current.decode("utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise DocumentationSyncError(
                f"Document could not be read before apply: {update.document}"
            ) from error

        if _digest(current) != update.original_sha256:
            raise DocumentationSyncError(
                f"Stale synchronization plan for document: {update.document}"
            )

        current_bounds = _marker_bounds(current_text, update.document)
        replacement_bounds = _marker_bounds(update.replacement_content, update.document)
        if current_bounds is None or replacement_bounds is None:
            raise DocumentationSyncError(
                f"Ownership markers invalid for document: {update.document}"
            )

        current_start, current_end = current_bounds
        replacement_start, replacement_end = replacement_bounds
        if current_text[:current_start] != update.replacement_content[:replacement_start]:
            raise DocumentationSyncError(
                f"Human-owned prefix changed in plan: {update.document}"
            )
        if current_text[current_end:] != update.replacement_content[replacement_end:]:
            raise DocumentationSyncError(
                f"Human-owned suffix changed in plan: {update.document}"
            )
        originals[update.document] = current
    return originals


def apply_documentation_sync(plan: DocumentationSyncPlan) -> DocumentationSyncResult:
    """Apply an approved plan after digest and ownership validation, then verify it."""

    _validate_plan(plan)
    _preflight(plan)

    changed: list[str] = []
    for update in plan.updates:
        path = plan.project_root / update.document
        try:
            path.write_bytes(update.replacement_content.encode("utf-8"))
        except OSError as error:
            raise DocumentationSyncError(
                f"Document write failed: {update.document}"
            ) from error
        changed.append(update.document)

    for update in plan.updates:
        path = plan.project_root / update.document
        try:
            written = path.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise DocumentationSyncError(
                f"Document verification read failed: {update.document}"
            ) from error
        if written != update.replacement_content:
            raise DocumentationSyncError(
                f"Document verification failed: {update.document}"
            )

    snapshot = inspect_project_state(ProjectInspectionRequest(plan.project_root))
    remaining = detect_documentation_drift(snapshot)
    changed_set = set(changed)
    unresolved = [item for item in remaining.items if item.document in changed_set]
    if unresolved:
        raise DocumentationSyncError(
            f"Post-apply drift remains for document: {unresolved[0].document}"
        )

    return DocumentationSyncResult(
        project_root=plan.project_root,
        changed_documents=tuple(changed),
    )
