from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_engineering.project_state_manifest import (
    CANONICAL_DOCUMENTS,
    DOCUMENT_PROJECTIONS,
    MANIFEST_RELATIVE_PATH,
    ManifestErrorReason,
    ProjectStateActivity,
    ProjectStateManifestError,
    build_project_state_manifest,
    load_project_state_manifest,
    parse_project_state_manifest,
)


def valid_mapping() -> dict[str, object]:
    return {
        "schema_version": 1,
        "completed_through": "AUTO-0019",
        "active_milestone": "AUTO-0020",
        "active_stage": "AUTO-0020-02",
        "active_state": "IMPLEMENTATION_ACTIVE",
        "release_line": "v0.2.0",
        "document_set_version": 1,
        "document_projections": {
            path: list(fields) for path, fields in DOCUMENT_PROJECTIONS
        },
    }


def quiescent_mapping() -> dict[str, object]:
    mapping = valid_mapping()
    mapping.update(
        {
            "schema_version": 2,
            "completed_through": "AUTO-0020",
            "active_milestone": None,
            "active_stage": None,
            "active_state": "QUIESCENT",
        }
    )
    return mapping


def assert_rejected(
    mapping: dict[str, object], reason: ManifestErrorReason
) -> None:
    with pytest.raises(ProjectStateManifestError) as captured:
        build_project_state_manifest(mapping)
    assert captured.value.reason is reason
    assert str(captured.value) == reason.value


def test_build_manifest_projects_strict_typed_state() -> None:
    state = build_project_state_manifest(valid_mapping())

    assert state.schema_version == 1
    assert state.completed_through == "AUTO-0019"
    assert state.active_milestone == "AUTO-0020"
    assert state.active_stage == "AUTO-0020-02"
    assert state.active_state is ProjectStateActivity.IMPLEMENTATION_ACTIVE
    assert state.release_line == "v0.2.0"
    assert state.document_set_version == 1
    paths = tuple(item.path for item in state.document_projections)
    assert paths == CANONICAL_DOCUMENTS
    assert not hasattr(state, "head_sha")
    assert not hasattr(state, "authority")


def test_tracked_manifest_loads_from_exact_portable_path() -> None:
    repository_root = Path(__file__).resolve().parents[2]

    state = load_project_state_manifest(repository_root)

    assert MANIFEST_RELATIVE_PATH == Path("docs/CANONICAL_PROJECT_STATE.json")
    assert state.schema_version == 2
    assert state.completed_through == "AUTO-0020"
    assert state.active_milestone == "AUTO-0021"
    assert state.active_stage == "AUTO-0021-01"
    assert state.active_state is ProjectStateActivity.DESIGN_ACTIVE


def test_schema_v2_projects_quiescent_terminal_state() -> None:
    state = build_project_state_manifest(quiescent_mapping())

    assert state.schema_version == 2
    assert state.completed_through == "AUTO-0020"
    assert state.active_milestone is None
    assert state.active_stage is None
    assert state.active_state is ProjectStateActivity.QUIESCENT


def test_schema_v2_preserves_active_state_contract() -> None:
    mapping = valid_mapping()
    mapping["schema_version"] = 2

    state = build_project_state_manifest(mapping)

    assert state.active_milestone == "AUTO-0020"
    assert state.active_stage == "AUTO-0020-02"
    assert state.active_state is ProjectStateActivity.IMPLEMENTATION_ACTIVE


def test_loading_manifest_is_read_only(tmp_path: Path) -> None:
    path = tmp_path / MANIFEST_RELATIVE_PATH
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(valid_mapping()), encoding="utf-8")
    before = path.read_bytes()

    first = load_project_state_manifest(tmp_path)
    second = load_project_state_manifest(tmp_path)

    assert first == second
    assert path.read_bytes() == before


def test_parser_is_independent_of_json_object_key_order() -> None:
    mapping = valid_mapping()
    reversed_mapping = dict(reversed(tuple(mapping.items())))

    assert parse_project_state_manifest(json.dumps(mapping)) == (
        parse_project_state_manifest(json.dumps(reversed_mapping))
    )


def test_parser_rejects_duplicate_keys_without_echoing_input() -> None:
    raw = '{"schema_version":1,"schema_version":1}'

    with pytest.raises(ProjectStateManifestError) as captured:
        parse_project_state_manifest(raw)

    assert captured.value.reason is ManifestErrorReason.DUPLICATE_KEY
    assert str(captured.value) == "duplicate_key"


@pytest.mark.parametrize("raw", ["[]", '"text"', "null"])
def test_parser_rejects_non_object_root(raw: str) -> None:
    with pytest.raises(ProjectStateManifestError) as captured:
        parse_project_state_manifest(raw)

    assert captured.value.reason is ManifestErrorReason.ROOT_NOT_OBJECT


def test_parser_rejects_malformed_json() -> None:
    with pytest.raises(ProjectStateManifestError) as captured:
        parse_project_state_manifest("{")

    assert captured.value.reason is ManifestErrorReason.MALFORMED_JSON


def test_parser_rejects_invalid_utf8() -> None:
    with pytest.raises(ProjectStateManifestError) as captured:
        parse_project_state_manifest(b"\xff")

    assert captured.value.reason is ManifestErrorReason.INVALID_UTF8


@pytest.mark.parametrize("key", ["schema_version", "active_stage"])
def test_manifest_rejects_missing_root_fields(key: str) -> None:
    mapping = valid_mapping()
    del mapping[key]

    assert_rejected(mapping, ManifestErrorReason.SCHEMA_FIELDS)


def test_manifest_rejects_unknown_root_fields() -> None:
    mapping = valid_mapping()
    mapping["token"] = "must-not-be-accepted"

    assert_rejected(mapping, ManifestErrorReason.SCHEMA_FIELDS)


@pytest.mark.parametrize("key", ["schema_version", "document_set_version"])
@pytest.mark.parametrize("value", [True, "1"])
def test_manifest_rejects_non_integer_versions(key: str, value: object) -> None:
    mapping = valid_mapping()
    mapping[key] = value

    assert_rejected(mapping, ManifestErrorReason.INVALID_FIELD_TYPE)


def test_manifest_rejects_unknown_schema_version() -> None:
    mapping = valid_mapping()
    mapping["schema_version"] = 3

    assert_rejected(mapping, ManifestErrorReason.UNSUPPORTED_SCHEMA)


def test_manifest_rejects_unknown_document_set_version() -> None:
    mapping = valid_mapping()
    mapping["document_set_version"] = 2

    assert_rejected(mapping, ManifestErrorReason.UNSUPPORTED_SCHEMA)


@pytest.mark.parametrize(
    ("schema_version", "active_milestone", "active_stage"),
    [
        (1, None, None),
        (2, "AUTO-0021", None),
        (2, None, "AUTO-0021-01"),
        (2, "AUTO-0021", "AUTO-0021-01"),
    ],
)
def test_quiescent_state_rejects_legacy_or_non_null_active_identity(
    schema_version: int,
    active_milestone: object,
    active_stage: object,
) -> None:
    mapping = quiescent_mapping()
    mapping["schema_version"] = schema_version
    mapping["active_milestone"] = active_milestone
    mapping["active_stage"] = active_stage

    assert_rejected(mapping, ManifestErrorReason.INVALID_FIELD_VALUE)


@pytest.mark.parametrize("key", ["active_milestone", "active_stage"])
def test_active_schema_v2_state_requires_active_identity(key: str) -> None:
    mapping = valid_mapping()
    mapping["schema_version"] = 2
    mapping[key] = None

    assert_rejected(mapping, ManifestErrorReason.INVALID_FIELD_TYPE)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("completed_through", "AUTO-19"),
        ("active_milestone", "AUTO-0019"),
        ("active_milestone", "AUTO-0021"),
        ("active_stage", "AUTO-0019-02"),
        ("active_stage", "AUTO-0020-00"),
        ("active_state", "ACTIVE"),
        ("release_line", "0.2.0"),
    ],
)
def test_manifest_rejects_invalid_state_values(key: str, value: object) -> None:
    mapping = valid_mapping()
    mapping[key] = value

    assert_rejected(mapping, ManifestErrorReason.INVALID_FIELD_VALUE)


@pytest.mark.parametrize(
    "key",
    [
        "completed_through",
        "active_milestone",
        "active_stage",
        "active_state",
        "release_line",
    ],
)
def test_manifest_rejects_non_string_state_fields(key: str) -> None:
    mapping = valid_mapping()
    mapping[key] = 1

    assert_rejected(mapping, ManifestErrorReason.INVALID_FIELD_TYPE)


def test_manifest_requires_exact_canonical_document_set() -> None:
    mapping = valid_mapping()
    projections = mapping["document_projections"]
    assert isinstance(projections, dict)
    del projections["docs/PROJECT_MAP.md"]

    assert_rejected(mapping, ManifestErrorReason.DOCUMENT_SET)


def test_manifest_rejects_unknown_canonical_document() -> None:
    mapping = valid_mapping()
    projections = mapping["document_projections"]
    assert isinstance(projections, dict)
    projections["docs/SECRETS.md"] = ["active_milestone"]

    assert_rejected(mapping, ManifestErrorReason.DOCUMENT_SET)


@pytest.mark.parametrize(
    "fields",
    [
        "active_milestone",
        ["completed_through", 1],
        ["active_milestone"],
        ["completed_through", "active_milestone", "active_milestone"],
    ],
)
def test_manifest_rejects_noncanonical_document_projection(
    fields: object,
) -> None:
    mapping = valid_mapping()
    projections = mapping["document_projections"]
    assert isinstance(projections, dict)
    projections["docs/PROJECT_MAP.md"] = fields

    assert_rejected(mapping, ManifestErrorReason.DOCUMENT_PROJECTION)


def test_load_manifest_fails_closed_when_file_is_missing(tmp_path: Path) -> None:
    with pytest.raises(ProjectStateManifestError) as captured:
        load_project_state_manifest(tmp_path)

    assert captured.value.reason is ManifestErrorReason.READ_FAILED
