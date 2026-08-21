"""Strict canonical project-state manifest primitives for AUTO-0020/0021."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = 2
SUPPORTED_SCHEMA_VERSIONS = (1, 2)
DOCUMENT_SET_VERSION = 2
SUPPORTED_DOCUMENT_SET_VERSIONS = (1, DOCUMENT_SET_VERSION)
MANIFEST_RELATIVE_PATH = Path("docs/CANONICAL_PROJECT_STATE.json")

COMPLETED_THROUGH = "completed_through"
ACTIVE_MILESTONE = "active_milestone"
ACTIVE_STAGE = "active_stage"
ACTIVE_STATE = "active_state"
RELEASE_LINE = "release_line"

DOCUMENT_PROJECTIONS_V1: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "docs/AI_CHAT_START.md",
        (COMPLETED_THROUGH, ACTIVE_MILESTONE, ACTIVE_STAGE, ACTIVE_STATE),
    ),
    (
        "docs/PROJECT_CONTEXT.md",
        (COMPLETED_THROUGH, ACTIVE_MILESTONE, RELEASE_LINE),
    ),
    (
        "docs/PROJECT_MAP.md",
        (COMPLETED_THROUGH, ACTIVE_MILESTONE),
    ),
    (
        "docs/CURRENT_STATUS.md",
        (
            COMPLETED_THROUGH,
            ACTIVE_MILESTONE,
            ACTIVE_STAGE,
            ACTIVE_STATE,
            RELEASE_LINE,
        ),
    ),
    (
        "docs/ROADMAP.md",
        (COMPLETED_THROUGH, ACTIVE_MILESTONE, ACTIVE_STAGE, ACTIVE_STATE),
    ),
    (
        "docs/MASTER_INDEX.md",
        (COMPLETED_THROUGH, ACTIVE_MILESTONE, ACTIVE_STAGE, ACTIVE_STATE),
    ),
)
DOCUMENT_PROJECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "README.md",
        (
            COMPLETED_THROUGH,
            ACTIVE_MILESTONE,
            ACTIVE_STAGE,
            ACTIVE_STATE,
            RELEASE_LINE,
        ),
    ),
    *DOCUMENT_PROJECTIONS_V1,
)
CANONICAL_DOCUMENTS_V1 = tuple(
    path for path, _fields in DOCUMENT_PROJECTIONS_V1
)
CANONICAL_DOCUMENTS = tuple(path for path, _fields in DOCUMENT_PROJECTIONS)
_DOCUMENT_PROJECTIONS_BY_VERSION = {
    1: DOCUMENT_PROJECTIONS_V1,
    2: DOCUMENT_PROJECTIONS,
}

_ROOT_KEYS = {
    "schema_version",
    COMPLETED_THROUGH,
    ACTIVE_MILESTONE,
    ACTIVE_STAGE,
    ACTIVE_STATE,
    RELEASE_LINE,
    "document_set_version",
    "document_projections",
}
_MILESTONE_RE = re.compile(r"^AUTO-(\d{4})$")
_STAGE_RE = re.compile(r"^AUTO-(\d{4})-(\d{2})$")
_RELEASE_RE = re.compile(r"^v\d+\.\d+\.\d+$")


class ProjectStateActivity(str, Enum):
    """Supported current-state lifecycle categories."""

    DESIGN_ACTIVE = "DESIGN_ACTIVE"
    IMPLEMENTATION_ACTIVE = "IMPLEMENTATION_ACTIVE"
    EVIDENCE_ACTIVE = "EVIDENCE_ACTIVE"
    FINAL_RECONCILIATION_ACTIVE = "FINAL_RECONCILIATION_ACTIVE"
    QUIESCENT = "QUIESCENT"


class ManifestErrorReason(str, Enum):
    """Stable fail-closed manifest rejection categories."""

    READ_FAILED = "read_failed"
    INVALID_UTF8 = "invalid_utf8"
    MALFORMED_JSON = "malformed_json"
    DUPLICATE_KEY = "duplicate_key"
    ROOT_NOT_OBJECT = "root_not_object"
    SCHEMA_FIELDS = "schema_fields"
    UNSUPPORTED_SCHEMA = "unsupported_schema"
    INVALID_FIELD_TYPE = "invalid_field_type"
    INVALID_FIELD_VALUE = "invalid_field_value"
    DOCUMENT_SET = "document_set"
    DOCUMENT_PROJECTION = "document_projection"


class ProjectStateManifestError(ValueError):
    """Raised when canonical project-state input fails closed."""

    def __init__(self, reason: ManifestErrorReason) -> None:
        self.reason = reason
        super().__init__(reason.value)


@dataclass(frozen=True, slots=True)
class DocumentProjection:
    """Required canonical-state fields for one governed document."""

    path: str
    fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CanonicalProjectState:
    """Validated minimal current-state identity for the repository."""

    schema_version: int
    completed_through: str
    active_milestone: str | None
    active_stage: str | None
    active_state: ProjectStateActivity
    release_line: str
    document_set_version: int
    document_projections: tuple[DocumentProjection, ...]


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProjectStateManifestError(ManifestErrorReason.DUPLICATE_KEY)
        result[key] = value
    return result


def _require_document_set_version(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProjectStateManifestError(ManifestErrorReason.INVALID_FIELD_TYPE)
    if value not in SUPPORTED_DOCUMENT_SET_VERSIONS:
        raise ProjectStateManifestError(ManifestErrorReason.UNSUPPORTED_SCHEMA)
    return value


def _require_schema_version(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProjectStateManifestError(ManifestErrorReason.INVALID_FIELD_TYPE)
    if value not in SUPPORTED_SCHEMA_VERSIONS:
        raise ProjectStateManifestError(ManifestErrorReason.UNSUPPORTED_SCHEMA)
    return value


def _require_string(value: Any) -> str:
    if not isinstance(value, str):
        raise ProjectStateManifestError(ManifestErrorReason.INVALID_FIELD_TYPE)
    return value


def _require_milestone(value: Any) -> tuple[str, int]:
    text = _require_string(value)
    match = _MILESTONE_RE.fullmatch(text)
    if match is None:
        raise ProjectStateManifestError(ManifestErrorReason.INVALID_FIELD_VALUE)
    return text, int(match.group(1))


def _require_stage(value: Any, active_number: int) -> str:
    text = _require_string(value)
    match = _STAGE_RE.fullmatch(text)
    if match is None or int(match.group(1)) != active_number:
        raise ProjectStateManifestError(ManifestErrorReason.INVALID_FIELD_VALUE)
    if int(match.group(2)) <= 0:
        raise ProjectStateManifestError(ManifestErrorReason.INVALID_FIELD_VALUE)
    return text


def _require_activity(value: Any) -> ProjectStateActivity:
    text = _require_string(value)
    try:
        return ProjectStateActivity(text)
    except ValueError as exc:
        raise ProjectStateManifestError(
            ManifestErrorReason.INVALID_FIELD_VALUE
        ) from exc


def _require_release_line(value: Any) -> str:
    text = _require_string(value)
    if _RELEASE_RE.fullmatch(text) is None:
        raise ProjectStateManifestError(ManifestErrorReason.INVALID_FIELD_VALUE)
    return text


def _require_document_projections(
    value: Any, document_set_version: int
) -> tuple[DocumentProjection, ...]:
    if not isinstance(value, dict):
        raise ProjectStateManifestError(ManifestErrorReason.INVALID_FIELD_TYPE)
    expected_projections = _DOCUMENT_PROJECTIONS_BY_VERSION[
        document_set_version
    ]
    canonical_documents = tuple(path for path, _fields in expected_projections)
    if set(value) != set(canonical_documents):
        raise ProjectStateManifestError(ManifestErrorReason.DOCUMENT_SET)

    expected_by_path = dict(expected_projections)
    projections: list[DocumentProjection] = []
    for path in canonical_documents:
        fields = value[path]
        if not isinstance(fields, list) or not all(
            isinstance(field, str) for field in fields
        ):
            raise ProjectStateManifestError(
                ManifestErrorReason.DOCUMENT_PROJECTION
            )
        projected = tuple(fields)
        if projected != expected_by_path[path]:
            raise ProjectStateManifestError(
                ManifestErrorReason.DOCUMENT_PROJECTION
            )
        projections.append(DocumentProjection(path=path, fields=projected))
    return tuple(projections)


def build_project_state_manifest(
    mapping: Mapping[str, Any],
) -> CanonicalProjectState:
    """Build one strict manifest from an already-decoded JSON object."""

    if set(mapping) != _ROOT_KEYS:
        raise ProjectStateManifestError(ManifestErrorReason.SCHEMA_FIELDS)

    schema_version = _require_schema_version(mapping["schema_version"])
    document_set_version = _require_document_set_version(
        mapping["document_set_version"]
    )
    if schema_version == 1 and document_set_version != 1:
        raise ProjectStateManifestError(ManifestErrorReason.DOCUMENT_SET)
    completed_through, completed_number = _require_milestone(
        mapping[COMPLETED_THROUGH]
    )
    active_state = _require_activity(mapping[ACTIVE_STATE])
    active_milestone: str | None
    active_stage: str | None
    if active_state is ProjectStateActivity.QUIESCENT:
        if (
            schema_version != 2
            or mapping[ACTIVE_MILESTONE] is not None
            or mapping[ACTIVE_STAGE] is not None
        ):
            raise ProjectStateManifestError(
                ManifestErrorReason.INVALID_FIELD_VALUE
            )
        active_milestone = None
        active_stage = None
    else:
        active_milestone, active_number = _require_milestone(
            mapping[ACTIVE_MILESTONE]
        )
        if active_number != completed_number + 1:
            raise ProjectStateManifestError(
                ManifestErrorReason.INVALID_FIELD_VALUE
            )
        active_stage = _require_stage(mapping[ACTIVE_STAGE], active_number)

    return CanonicalProjectState(
        schema_version=schema_version,
        completed_through=completed_through,
        active_milestone=active_milestone,
        active_stage=active_stage,
        active_state=active_state,
        release_line=_require_release_line(mapping[RELEASE_LINE]),
        document_set_version=document_set_version,
        document_projections=_require_document_projections(
            mapping["document_projections"], document_set_version
        ),
    )


def parse_project_state_manifest(data: str | bytes) -> CanonicalProjectState:
    """Parse strict UTF-8 JSON with duplicate-key rejection."""

    if isinstance(data, bytes):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ProjectStateManifestError(
                ManifestErrorReason.INVALID_UTF8
            ) from exc
    elif isinstance(data, str):
        text = data
    else:
        raise ProjectStateManifestError(ManifestErrorReason.INVALID_FIELD_TYPE)

    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except json.JSONDecodeError as exc:
        raise ProjectStateManifestError(ManifestErrorReason.MALFORMED_JSON) from exc
    if not isinstance(value, dict):
        raise ProjectStateManifestError(ManifestErrorReason.ROOT_NOT_OBJECT)
    return build_project_state_manifest(value)


def load_project_state_manifest(repository_root: Path) -> CanonicalProjectState:
    """Load the repository manifest from its one portable relative path."""

    path = repository_root / MANIFEST_RELATIVE_PATH
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ProjectStateManifestError(ManifestErrorReason.READ_FAILED) from exc
    return parse_project_state_manifest(data)
