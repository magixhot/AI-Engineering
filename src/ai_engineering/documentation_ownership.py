"""Read-only AUTO-0003 documentation ownership classification and planning."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .documentation_sync import (
    DocumentationSyncError,
    _expected_body,
    _markers,
)
from .project_inspection import ProjectStateSnapshot

ELIGIBLE_DOCUMENTS = (
    "CURRENT_STATUS.md",
    "MASTER_INDEX.md",
    "PROJECT_MAP.md",
)

OwnershipState = Literal[
    "initialized",
    "missing",
    "partial",
    "duplicate",
    "malformed",
    "unsupported",
    "missing_document",
]


class DocumentationOwnershipError(RuntimeError):
    """Raised when ownership initialization cannot be planned safely."""


@dataclass(frozen=True)
class DocumentationOwnershipClassification:
    document: str
    state: OwnershipState
    reason: str


@dataclass(frozen=True)
class DocumentationOwnershipInitializationUpdate:
    document: str
    original_sha256: str
    replacement_content: str
    state: OwnershipState


@dataclass(frozen=True)
class DocumentationOwnershipInitializationPlan:
    project_root: Path
    updates: tuple[DocumentationOwnershipInitializationUpdate, ...]
    classifications: tuple[DocumentationOwnershipClassification, ...]
    manual_review: tuple[str, ...]


def _newline_state(content: str) -> tuple[str | None, str | None]:
    crlf_count = content.count("\r\n")
    bare_lf_count = content.count("\n") - crlf_count
    if crlf_count and bare_lf_count:
        return None, "mixed newline conventions"
    if crlf_count:
        return "\r\n", None
    return "\n", None


def classify_document_ownership(
    document: str,
    content: str,
) -> DocumentationOwnershipClassification:
    """Classify exact AUTO-0002 marker ownership without mutating content."""

    if document not in ELIGIBLE_DOCUMENTS:
        return DocumentationOwnershipClassification(
            document, "unsupported", "document is outside AUTO-0003 V1 scope"
        )

    start_marker, end_marker = _markers(document)
    start_count = content.count(start_marker)
    end_count = content.count(end_marker)

    if start_count > 1 or end_count > 1:
        return DocumentationOwnershipClassification(
            document, "duplicate", "one or both ownership markers are duplicated"
        )
    if (start_count, end_count) in {(1, 0), (0, 1)}:
        return DocumentationOwnershipClassification(
            document, "partial", "only one ownership marker is present"
        )
    if start_count == 1 and end_count == 1:
        if content.find(end_marker) <= content.find(start_marker):
            return DocumentationOwnershipClassification(
                document, "malformed", "ownership markers are out of order"
            )
        return DocumentationOwnershipClassification(
            document, "initialized", "valid ownership marker pair is present"
        )

    marker_prefix = "<!-- ai-engineering:auto0002:"
    if marker_prefix in content:
        return DocumentationOwnershipClassification(
            document,
            "unsupported",
            "unrecognized AUTO-0002 marker-like content requires manual review",
        )

    _, newline_error = _newline_state(content)
    if newline_error is not None:
        return DocumentationOwnershipClassification(
            document, "unsupported", newline_error
        )

    return DocumentationOwnershipClassification(
        document, "missing", "approved ownership markers are absent"
    )


def _read_content(root: Path, document: str) -> str | None:
    path = root / document
    try:
        return path.read_bytes().decode("utf-8")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as error:
        raise DocumentationOwnershipError(
            f"Document could not be read: {document}"
        ) from error


def _insert_at_eof(
    snapshot: ProjectStateSnapshot,
    document: str,
    content: str,
) -> str:
    """Append the document-specific V1 managed section at the EOF boundary."""

    newline, error = _newline_state(content)
    if newline is None or error is not None:
        raise DocumentationOwnershipError(
            f"Unsupported newline state for {document}: {error}"
        )

    start_marker, end_marker = _markers(document)
    try:
        body = _expected_body(snapshot, document, content)
    except DocumentationSyncError as error:
        raise DocumentationOwnershipError(
            f"Managed section could not be rendered: {document}"
        ) from error

    # EOF is the explicit V1 insertion boundary for each approved document.
    # Existing bytes are never rewritten; separators are added after them only.
    separator = "" if not content or content.endswith(("\n", "\r")) else newline
    if content and not content.endswith(newline * 2):
        separator += newline
    return content + separator + start_marker + body + end_marker + newline


def plan_documentation_ownership_initialization(
    snapshot: ProjectStateSnapshot,
    documents: tuple[str, ...] = ELIGIBLE_DOCUMENTS,
) -> DocumentationOwnershipInitializationPlan:
    """Return a deterministic AUTO-0003 initialization plan without writes."""

    root = snapshot.project_root.resolve()
    if not documents:
        return DocumentationOwnershipInitializationPlan(root, (), (), ())
    if len(set(documents)) != len(documents):
        raise DocumentationOwnershipError("Duplicate document selection is not allowed")
    unsupported = tuple(name for name in documents if name not in ELIGIBLE_DOCUMENTS)
    if unsupported:
        raise DocumentationOwnershipError(
            f"Unsupported document selection: {', '.join(unsupported)}"
        )

    updates: list[DocumentationOwnershipInitializationUpdate] = []
    classifications: list[DocumentationOwnershipClassification] = []
    manual_review: list[str] = []

    for document in ELIGIBLE_DOCUMENTS:
        if document not in documents:
            continue
        content = _read_content(root, document)
        if content is None:
            classification = DocumentationOwnershipClassification(
                document, "missing_document", "approved target file does not exist"
            )
        else:
            classification = classify_document_ownership(document, content)
        classifications.append(classification)

        if classification.state == "missing" and content is not None:
            replacement = _insert_at_eof(snapshot, document, content)
            updates.append(
                DocumentationOwnershipInitializationUpdate(
                    document=document,
                    original_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                    replacement_content=replacement,
                    state="missing",
                )
            )
        elif classification.state != "initialized":
            manual_review.append(document)

    return DocumentationOwnershipInitializationPlan(
        project_root=root,
        updates=tuple(updates),
        classifications=tuple(classifications),
        manual_review=tuple(manual_review),
    )
