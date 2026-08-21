from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_engineering.project_state_coherence import (
    MARKER_CLOSE,
    MARKER_OPEN,
    CoherenceIssue,
    CoherenceReason,
    main,
    serialize_coherence_report,
    validate_project_state_coherence,
)
from ai_engineering.project_state_manifest import (
    ACTIVE_MILESTONE,
    ACTIVE_STAGE,
    ACTIVE_STATE,
    COMPLETED_THROUGH,
    DOCUMENT_PROJECTIONS,
    MANIFEST_RELATIVE_PATH,
    RELEASE_LINE,
    ManifestErrorReason,
)


def valid_mapping() -> dict[str, object]:
    return {
        "schema_version": 1,
        "completed_through": "AUTO-0019",
        "active_milestone": "AUTO-0020",
        "active_stage": "AUTO-0020-03",
        "active_state": "IMPLEMENTATION_ACTIVE",
        "release_line": "v0.2.0",
        "document_set_version": 1,
        "document_projections": {
            path: list(fields) for path, fields in DOCUMENT_PROJECTIONS
        },
    }


def state_values() -> dict[str, str]:
    return {
        COMPLETED_THROUGH: "AUTO-0019",
        ACTIVE_MILESTONE: "AUTO-0020",
        ACTIVE_STAGE: "AUTO-0020-03",
        ACTIVE_STATE: "IMPLEMENTATION_ACTIVE",
        RELEASE_LINE: "v0.2.0",
    }


def marker_for(path: str, **overrides: object) -> str:
    fields = dict(DOCUMENT_PROJECTIONS)[path]
    values = state_values()
    marker: dict[str, object] = {"schema_version": 1}
    marker.update({field: values[field] for field in fields})
    marker.update(overrides)
    return MARKER_OPEN + json.dumps(marker, sort_keys=True) + MARKER_CLOSE


def write_fixture(root: Path) -> None:
    manifest_path = root / MANIFEST_RELATIVE_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(valid_mapping(), indent=2) + "\n", encoding="utf-8"
    )
    for path, _fields in DOCUMENT_PROJECTIONS:
        document = root / path
        document.parent.mkdir(parents=True, exist_ok=True)
        document.write_text(
            f"# Canonical document\n\n{marker_for(path)}\n\n"
            "Historical evidence: AUTO-0014-06 was once active.\n",
            encoding="utf-8",
        )


def replace_marker(root: Path, path: str, marker: str) -> None:
    document = root / path
    document.write_text(
        f"# Canonical document\n\n{marker}\n\nHistorical prose.\n",
        encoding="utf-8",
    )


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def test_coherent_fixture_passes_with_historical_prose_ignored(
    tmp_path: Path,
) -> None:
    write_fixture(tmp_path)

    report = validate_project_state_coherence(tmp_path)

    assert report.coherent is True
    assert report.issues == ()
    assert serialize_coherence_report(report) == '{"coherent":true,"issues":[]}'


def test_tracked_canonical_document_set_is_coherent() -> None:
    repository_root = Path(__file__).resolve().parents[2]

    report = validate_project_state_coherence(repository_root)

    assert report.coherent is True
    assert report.issues == ()


def test_cli_returns_success_with_bounded_report(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repository_root = Path(__file__).resolve().parents[2]

    result = main([str(repository_root)])

    captured = capsys.readouterr()
    assert result == 0
    assert captured.out == '{"coherent":true,"issues":[]}\n'
    assert captured.err == ""


def test_cli_failure_does_not_expose_local_root(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main([str(tmp_path)])

    captured = capsys.readouterr()
    assert result == 1
    assert str(tmp_path) not in captured.out
    assert json.loads(captured.out) == {
        "coherent": False,
        "issues": [
            {
                "manifest_reason": "read_failed",
                "path": "docs/CANONICAL_PROJECT_STATE.json",
                "reason": "manifest_invalid",
            }
        ],
    }
    assert captured.err == ""


def test_cli_rejects_extra_arguments_deterministically(
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main([".", "extra"])

    captured = capsys.readouterr()
    assert result == 2
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "coherent": False,
        "issues": [
            {
                "path": "docs/CANONICAL_PROJECT_STATE.json",
                "reason": "invalid_arguments",
            }
        ],
    }


def test_quality_workflow_invokes_offline_coherence_gate() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    workflow = (repository_root / ".github/workflows/quality.yml").read_text(
        encoding="utf-8"
    )

    assert workflow.count(
        "uv run python -B -m ai_engineering.project_state_coherence ."
    ) == 1
    assert workflow.index("Verify canonical project-state coherence") < (
        workflow.index("uv run python -m ruff check .")
    )
    assert "uv run python -m ruff check ." in workflow
    assert "uv run python -m mypy src tests" in workflow
    assert "uv run python -m pytest" in workflow
    assert "python -m ai_engineering.quality_verifier" in workflow


def test_validation_is_deterministic_and_read_only(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    before = snapshot(tmp_path)

    first = validate_project_state_coherence(tmp_path)
    second = validate_project_state_coherence(tmp_path)

    assert first == second
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("path", [path for path, _ in DOCUMENT_PROJECTIONS])
def test_each_missing_document_fails_closed(tmp_path: Path, path: str) -> None:
    write_fixture(tmp_path)
    (tmp_path / path).unlink()

    report = validate_project_state_coherence(tmp_path)

    assert report.issues == (
        CoherenceIssue(
            path=path,
            reason=CoherenceReason.DOCUMENT_READ_FAILED,
        ),
    )


def test_document_directory_is_rejected(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    path = "docs/PROJECT_MAP.md"
    document = tmp_path / path
    document.unlink()
    document.mkdir()

    report = validate_project_state_coherence(tmp_path)

    assert report.issues[0].path == path
    assert report.issues[0].reason is CoherenceReason.DOCUMENT_TYPE


def test_document_symlink_is_rejected(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    path = "docs/PROJECT_MAP.md"
    document = tmp_path / path
    target = tmp_path / "target.md"
    target.write_text(marker_for(path), encoding="utf-8")
    document.unlink()
    document.symlink_to(target)

    report = validate_project_state_coherence(tmp_path)

    assert report.issues[0].path == path
    assert report.issues[0].reason is CoherenceReason.DOCUMENT_TYPE


def test_invalid_document_utf8_is_rejected(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    path = "docs/PROJECT_MAP.md"
    (tmp_path / path).write_bytes(b"\xff")

    report = validate_project_state_coherence(tmp_path)

    assert report.issues[0].path == path
    assert report.issues[0].reason is CoherenceReason.INVALID_UTF8


@pytest.mark.parametrize(
    ("marker", "reason"),
    [
        ("No state marker.", CoherenceReason.MARKER_MISSING),
        (MARKER_OPEN + "{" + MARKER_CLOSE, CoherenceReason.MARKER_MALFORMED),
        (MARKER_OPEN + "[]" + MARKER_CLOSE, CoherenceReason.MARKER_MALFORMED),
    ],
)
def test_missing_or_malformed_marker_is_rejected(
    tmp_path: Path,
    marker: str,
    reason: CoherenceReason,
) -> None:
    write_fixture(tmp_path)
    path = "docs/PROJECT_MAP.md"
    replace_marker(tmp_path, path, marker)

    report = validate_project_state_coherence(tmp_path)

    assert report.issues[0].path == path
    assert report.issues[0].reason is reason


def test_duplicate_marker_is_rejected(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    path = "docs/PROJECT_MAP.md"
    marker = marker_for(path)
    replace_marker(tmp_path, path, marker + "\n" + marker)

    report = validate_project_state_coherence(tmp_path)

    assert report.issues[0].reason is CoherenceReason.MARKER_DUPLICATE


def test_duplicate_marker_key_is_rejected_without_echoing_content(
    tmp_path: Path,
) -> None:
    write_fixture(tmp_path)
    path = "docs/PROJECT_MAP.md"
    payload = (
        '{"schema_version":1,"completed_through":"AUTO-0019",'
        '"active_milestone":"AUTO-0020",'
        '"active_milestone":"secret-value"}'
    )
    replace_marker(tmp_path, path, MARKER_OPEN + payload + MARKER_CLOSE)

    report = validate_project_state_coherence(tmp_path)
    serialized = serialize_coherence_report(report)

    assert report.issues[0].reason is CoherenceReason.MARKER_DUPLICATE_KEY
    assert "secret-value" not in serialized


@pytest.mark.parametrize(
    "marker",
    [
        marker_for("docs/PROJECT_MAP.md", token="must-not-be-accepted"),
        MARKER_OPEN
        + json.dumps(
            {
                "schema_version": 1,
                "active_milestone": "AUTO-0020",
            }
        )
        + MARKER_CLOSE,
    ],
)
def test_marker_requires_exact_projected_fields(
    tmp_path: Path, marker: str
) -> None:
    write_fixture(tmp_path)
    path = "docs/PROJECT_MAP.md"
    replace_marker(tmp_path, path, marker)

    report = validate_project_state_coherence(tmp_path)

    assert report.issues[0].reason is CoherenceReason.MARKER_FIELDS


@pytest.mark.parametrize(
    ("path", "field", "value"),
    [
        ("docs/PROJECT_MAP.md", "schema_version", 2),
        ("docs/PROJECT_MAP.md", COMPLETED_THROUGH, "AUTO-0018"),
        ("docs/PROJECT_MAP.md", ACTIVE_MILESTONE, "AUTO-0019"),
        ("docs/AI_CHAT_START.md", ACTIVE_STAGE, "AUTO-0020-02"),
        ("docs/AI_CHAT_START.md", ACTIVE_STATE, "DESIGN_ACTIVE"),
        ("docs/PROJECT_CONTEXT.md", RELEASE_LINE, "v0.1.0"),
    ],
)
def test_marker_mismatch_identifies_only_stable_field(
    tmp_path: Path,
    path: str,
    field: str,
    value: object,
) -> None:
    write_fixture(tmp_path)
    replace_marker(tmp_path, path, marker_for(path, **{field: value}))

    report = validate_project_state_coherence(tmp_path)
    serialized = serialize_coherence_report(report)

    assert report.issues[0].path == path
    assert report.issues[0].reason is CoherenceReason.MARKER_MISMATCH
    assert report.issues[0].field == field
    assert str(value) not in serialized


def test_multiple_findings_follow_canonical_document_order(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    (tmp_path / "docs/AI_CHAT_START.md").unlink()
    (tmp_path / "docs/PROJECT_MAP.md").write_text("missing marker", encoding="utf-8")

    report = validate_project_state_coherence(tmp_path)

    assert tuple(issue.path for issue in report.issues) == (
        "docs/AI_CHAT_START.md",
        "docs/PROJECT_MAP.md",
    )


def test_invalid_manifest_returns_one_bounded_issue(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    (tmp_path / MANIFEST_RELATIVE_PATH).write_text("{", encoding="utf-8")

    report = validate_project_state_coherence(tmp_path)
    serialized = serialize_coherence_report(report)

    assert report.coherent is False
    assert len(report.issues) == 1
    assert report.issues[0].path == MANIFEST_RELATIVE_PATH.as_posix()
    assert report.issues[0].reason is CoherenceReason.MANIFEST_INVALID
    assert report.issues[0].manifest_reason is ManifestErrorReason.MALFORMED_JSON
    assert serialized == (
        '{"coherent":false,"issues":[{"manifest_reason":"malformed_json",'
        '"path":"docs/CANONICAL_PROJECT_STATE.json",'
        '"reason":"manifest_invalid"}]}'
    )


def test_manifest_symlink_is_rejected_without_following_it(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    manifest = tmp_path / MANIFEST_RELATIVE_PATH
    target = tmp_path / "manifest-target.json"
    target.write_bytes(manifest.read_bytes())
    manifest.unlink()
    manifest.symlink_to(target)

    report = validate_project_state_coherence(tmp_path)

    assert report.issues[0].reason is CoherenceReason.MANIFEST_INVALID
    assert report.issues[0].manifest_reason is ManifestErrorReason.READ_FAILED
