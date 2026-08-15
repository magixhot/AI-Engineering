"""AUTO-0003 documentation ownership classification, planning, and apply."""

from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .documentation_sync import (
    DocumentationSyncError,
    _expected_body,
    _markers,
    detect_documentation_drift,
)
from .project_inspection import (
    ProjectInspectionRequest,
    ProjectStateSnapshot,
    inspect_project_state,
)

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
    """Raised when ownership initialization cannot proceed safely."""


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


@dataclass(frozen=True)
class DocumentationOwnershipInitializationResult:
    project_root: Path
    changed_documents: tuple[str, ...]


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


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
        raise DocumentationOwnershipError(
            "Duplicate document selection is not allowed"
        )
    unsupported = tuple(
        name for name in documents if name not in ELIGIBLE_DOCUMENTS
    )
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
                document,
                "missing_document",
                "approved target file does not exist",
            )
        else:
            classification = classify_document_ownership(document, content)
        classifications.append(classification)

        if classification.state == "missing" and content is not None:
            replacement = _insert_at_eof(snapshot, document, content)
            updates.append(
                DocumentationOwnershipInitializationUpdate(
                    document=document,
                    original_sha256=hashlib.sha256(
                        content.encode("utf-8")
                    ).hexdigest(),
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


def _validate_apply_plan(
    plan: DocumentationOwnershipInitializationPlan,
) -> None:
    if plan.manual_review:
        raise DocumentationOwnershipError(
            "Initialization plan requires manual review before apply"
        )

    documents = [update.document for update in plan.updates]
    if len(documents) != len(set(documents)):
        raise DocumentationOwnershipError(
            "Initialization plan contains duplicate documents"
        )

    unsupported = sorted(set(documents) - set(ELIGIBLE_DOCUMENTS))
    if unsupported:
        raise DocumentationOwnershipError(
            f"Initialization plan contains unsupported document: {unsupported[0]}"
        )

    invalid_state = next(
        (update.document for update in plan.updates if update.state != "missing"),
        None,
    )
    if invalid_state is not None:
        raise DocumentationOwnershipError(
            f"Initialization update has invalid source state: {invalid_state}"
        )


def _preflight_apply(
    plan: DocumentationOwnershipInitializationPlan,
) -> dict[str, bytes]:
    originals: dict[str, bytes] = {}
    root = plan.project_root.resolve()

    for update in plan.updates:
        path = root / update.document
        try:
            current = path.read_bytes()
            current_text = current.decode("utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise DocumentationOwnershipError(
                f"Document could not be read before apply: {update.document}"
            ) from error

        if _digest(current) != update.original_sha256:
            raise DocumentationOwnershipError(
                f"Stale initialization plan for document: {update.document}"
            )

        current_state = classify_document_ownership(
            update.document,
            current_text,
        )
        if current_state.state != "missing":
            raise DocumentationOwnershipError(
                f"Ownership state changed before apply: {update.document}"
            )

        replacement_state = classify_document_ownership(
            update.document,
            update.replacement_content,
        )
        if replacement_state.state != "initialized":
            raise DocumentationOwnershipError(
                f"Replacement ownership markers invalid: {update.document}"
            )

        replacement_bytes = update.replacement_content.encode("utf-8")
        if not replacement_bytes.startswith(current):
            raise DocumentationOwnershipError(
                f"Human-authored bytes changed in plan: {update.document}"
            )
        originals[update.document] = current

    return originals


def _stage_bytes(path: Path, content: bytes) -> Path:
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".auto0003.tmp",
            dir=path.parent,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        return temporary_path
    except OSError as error:
        raise DocumentationOwnershipError(
            f"Document staging failed: {path.name}"
        ) from error


def _cleanup_staged(paths: list[Path]) -> None:
    for path in paths:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def _restore_originals(
    root: Path,
    originals: dict[str, bytes],
    documents: tuple[str, ...],
) -> None:
    staged: list[Path] = []
    try:
        for document in documents:
            path = root / document
            temporary = _stage_bytes(path, originals[document])
            staged.append(temporary)
        for document, temporary in zip(documents, staged, strict=True):
            os.replace(temporary, root / document)
    except (OSError, DocumentationOwnershipError) as error:
        raise DocumentationOwnershipError(
            "Initialization rollback failed after apply error"
        ) from error
    finally:
        _cleanup_staged(staged)


def _verify_applied_plan(
    plan: DocumentationOwnershipInitializationPlan,
) -> None:
    root = plan.project_root.resolve()
    for update in plan.updates:
        path = root / update.document
        try:
            written = path.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise DocumentationOwnershipError(
                f"Document verification read failed: {update.document}"
            ) from error
        if written != update.replacement_content:
            raise DocumentationOwnershipError(
                f"Document verification failed: {update.document}"
            )
        classification = classify_document_ownership(
            update.document,
            written,
        )
        if classification.state != "initialized":
            raise DocumentationOwnershipError(
                f"Document ownership verification failed: {update.document}"
            )

    snapshot = inspect_project_state(ProjectInspectionRequest(root))
    remaining = detect_documentation_drift(snapshot)
    changed = {update.document for update in plan.updates}
    unresolved = [
        item for item in remaining.items if item.document in changed
    ]
    if unresolved:
        raise DocumentationOwnershipError(
            f"AUTO-0002 handoff verification failed: {unresolved[0].document}"
        )

    follow_up = plan_documentation_ownership_initialization(
        snapshot,
        tuple(update.document for update in plan.updates),
    )
    if follow_up.updates or follow_up.manual_review:
        raise DocumentationOwnershipError(
            "AUTO-0003 idempotency verification failed"
        )
    if any(
        item.state != "initialized" for item in follow_up.classifications
    ):
        raise DocumentationOwnershipError(
            "AUTO-0003 ownership verification failed after apply"
        )


def apply_documentation_ownership_initialization(
    plan: DocumentationOwnershipInitializationPlan,
) -> DocumentationOwnershipInitializationResult:
    """Apply a guarded AUTO-0003 plan and verify AUTO-0002 handoff."""

    _validate_apply_plan(plan)
    originals = _preflight_apply(plan)
    root = plan.project_root.resolve()
    if not plan.updates:
        return DocumentationOwnershipInitializationResult(root, ())

    staged: list[Path] = []
    replaced: list[str] = []
    documents = tuple(update.document for update in plan.updates)
    try:
        for update in plan.updates:
            path = root / update.document
            staged.append(
                _stage_bytes(path, update.replacement_content.encode("utf-8"))
            )

        for update, temporary in zip(plan.updates, staged, strict=True):
            os.replace(temporary, root / update.document)
            replaced.append(update.document)

        _verify_applied_plan(plan)
    except (OSError, DocumentationOwnershipError) as error:
        if replaced:
            _restore_originals(root, originals, tuple(replaced))
        if isinstance(error, DocumentationOwnershipError):
            raise
        raise DocumentationOwnershipError(
            "Initialization apply failed while replacing documents"
        ) from error
    finally:
        _cleanup_staged(staged)

    return DocumentationOwnershipInitializationResult(
        project_root=root,
        changed_documents=documents,
    )
