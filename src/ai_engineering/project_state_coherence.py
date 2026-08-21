"""Read-only canonical project-state coherence validation for AUTO-0020/0021."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .project_state_manifest import (
    ACTIVE_MILESTONE,
    ACTIVE_STAGE,
    ACTIVE_STATE,
    COMPLETED_THROUGH,
    MANIFEST_RELATIVE_PATH,
    RELEASE_LINE,
    CanonicalProjectState,
    DocumentProjection,
    ManifestErrorReason,
    ProjectStateManifestError,
    load_project_state_manifest,
)

MARKER_OPEN = "<!-- canonical-project-state\n"
MARKER_CLOSE = "\n-->"


class CoherenceReason(str, Enum):
    """Stable bounded coherence failure categories."""

    MANIFEST_INVALID = "manifest_invalid"
    DOCUMENT_READ_FAILED = "document_read_failed"
    DOCUMENT_TYPE = "document_type"
    INVALID_UTF8 = "invalid_utf8"
    MARKER_MISSING = "marker_missing"
    MARKER_DUPLICATE = "marker_duplicate"
    MARKER_MALFORMED = "marker_malformed"
    MARKER_DUPLICATE_KEY = "marker_duplicate_key"
    MARKER_POSITION = "marker_position"
    MARKER_FIELDS = "marker_fields"
    MARKER_MISMATCH = "marker_mismatch"


@dataclass(frozen=True, slots=True)
class CoherenceIssue:
    """One public-safe repository-relative coherence finding."""

    path: str
    reason: CoherenceReason
    field: str | None = None
    manifest_reason: ManifestErrorReason | None = None


@dataclass(frozen=True, slots=True)
class CoherenceReport:
    """Deterministic read-only validation result."""

    issues: tuple[CoherenceIssue, ...]

    @property
    def coherent(self) -> bool:
        """Return whether every required document matches canonical state."""

        return not self.issues


class _MarkerError(ValueError):
    def __init__(
        self, reason: CoherenceReason, *, field: str | None = None
    ) -> None:
        self.reason = reason
        self.field = field
        super().__init__(reason.value)


def _reject_duplicate_marker_pairs(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _MarkerError(CoherenceReason.MARKER_DUPLICATE_KEY)
        result[key] = value
    return result


def _extract_marker(text: str) -> str:
    start = text.find(MARKER_OPEN)
    if start < 0:
        raise _MarkerError(CoherenceReason.MARKER_MISSING)
    if text.find(MARKER_OPEN, start + len(MARKER_OPEN)) >= 0:
        raise _MarkerError(CoherenceReason.MARKER_DUPLICATE)
    payload_start = start + len(MARKER_OPEN)
    end = text.find(MARKER_CLOSE, payload_start)
    if end < 0:
        raise _MarkerError(CoherenceReason.MARKER_MALFORMED)
    return text[payload_start:end]


def _parse_marker(text: str) -> dict[str, Any]:
    payload = _extract_marker(text)
    try:
        value = json.loads(payload, object_pairs_hook=_reject_duplicate_marker_pairs)
    except json.JSONDecodeError as exc:
        raise _MarkerError(CoherenceReason.MARKER_MALFORMED) from exc
    if not isinstance(value, dict):
        raise _MarkerError(CoherenceReason.MARKER_MALFORMED)
    return value


def _expected_values(state: CanonicalProjectState) -> dict[str, str | None]:
    return {
        COMPLETED_THROUGH: state.completed_through,
        ACTIVE_MILESTONE: state.active_milestone,
        ACTIVE_STAGE: state.active_stage,
        ACTIVE_STATE: state.active_state.value,
        RELEASE_LINE: state.release_line,
    }


def _validate_marker(
    text: str,
    state: CanonicalProjectState,
    projection: DocumentProjection,
) -> None:
    marker = _parse_marker(text)
    expected_fields = {"schema_version", *projection.fields}
    if set(marker) != expected_fields:
        raise _MarkerError(CoherenceReason.MARKER_FIELDS)
    schema_version = marker["schema_version"]
    if (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, int)
        or schema_version != state.schema_version
    ):
        raise _MarkerError(
            CoherenceReason.MARKER_MISMATCH, field="schema_version"
        )

    expected = _expected_values(state)
    for field in projection.fields:
        if marker[field] != expected[field]:
            raise _MarkerError(CoherenceReason.MARKER_MISMATCH, field=field)


def _validate_marker_position(
    text: str,
    state: CanonicalProjectState,
    projection: DocumentProjection,
) -> None:
    if state.document_set_version != 2 or projection.path != "README.md":
        return
    heading, separator, remainder = text.partition("\n")
    if (
        not separator
        or not heading.startswith("# ")
        or heading.startswith("##")
        or not remainder.startswith("\n" + MARKER_OPEN)
    ):
        raise _MarkerError(CoherenceReason.MARKER_POSITION)


def _manifest_issue(
    reason: ManifestErrorReason,
) -> CoherenceReport:
    return CoherenceReport(
        issues=(
            CoherenceIssue(
                path=MANIFEST_RELATIVE_PATH.as_posix(),
                reason=CoherenceReason.MANIFEST_INVALID,
                manifest_reason=reason,
            ),
        )
    )


def validate_project_state_coherence(repository_root: Path) -> CoherenceReport:
    """Validate all canonical documents without modifying repository state."""

    manifest_path = repository_root / MANIFEST_RELATIVE_PATH
    if manifest_path.is_symlink() or not manifest_path.is_file():
        return _manifest_issue(ManifestErrorReason.READ_FAILED)
    try:
        state = load_project_state_manifest(repository_root)
    except ProjectStateManifestError as exc:
        return _manifest_issue(exc.reason)

    issues: list[CoherenceIssue] = []
    for projection in state.document_projections:
        path = repository_root / projection.path
        if path.is_symlink() or (path.exists() and not path.is_file()):
            issues.append(
                CoherenceIssue(
                    path=projection.path,
                    reason=CoherenceReason.DOCUMENT_TYPE,
                )
            )
            continue
        try:
            data = path.read_bytes()
        except OSError:
            issues.append(
                CoherenceIssue(
                    path=projection.path,
                    reason=CoherenceReason.DOCUMENT_READ_FAILED,
                )
            )
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            issues.append(
                CoherenceIssue(
                    path=projection.path,
                    reason=CoherenceReason.INVALID_UTF8,
                )
            )
            continue
        try:
            _validate_marker(text, state, projection)
            _validate_marker_position(text, state, projection)
        except _MarkerError as exc:
            issues.append(
                CoherenceIssue(
                    path=projection.path,
                    reason=exc.reason,
                    field=exc.field,
                )
            )

    return CoherenceReport(issues=tuple(issues))


def serialize_coherence_report(report: CoherenceReport) -> str:
    """Serialize only bounded portable coherence evidence."""

    issues: list[dict[str, object]] = []
    for issue in report.issues:
        value: dict[str, object] = {
            "path": issue.path,
            "reason": issue.reason.value,
        }
        if issue.field is not None:
            value["field"] = issue.field
        if issue.manifest_reason is not None:
            value["manifest_reason"] = issue.manifest_reason.value
        issues.append(value)
    return json.dumps(
        {"coherent": report.coherent, "issues": issues},
        sort_keys=True,
        separators=(",", ":"),
    )


def main(argv: list[str] | None = None) -> int:
    """Run the offline coherence gate for one repository root."""

    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) > 1:
        print(
            '{"coherent":false,"issues":[{"path":"docs/'
            'CANONICAL_PROJECT_STATE.json","reason":"invalid_arguments"}]}',
            file=sys.stderr,
        )
        return 2
    repository_root = Path(arguments[0] if arguments else ".")
    report = validate_project_state_coherence(repository_root)
    print(serialize_coherence_report(report))
    return 0 if report.coherent else 1


if __name__ == "__main__":
    raise SystemExit(main())
