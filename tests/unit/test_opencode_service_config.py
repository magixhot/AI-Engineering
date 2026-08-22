from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering.opencode_service_config import (
    DEFAULT_POLL_SECONDS,
    ServiceConfigError,
    build_service_config,
    load_service_config,
    parse_service_config,
)


def valid_mapping() -> dict[str, object]:
    repository_root = Path.cwd().anchor or str(Path.cwd().resolve())
    if repository_root == Path.cwd().anchor:
        repository_root = str(Path(repository_root) / "workspace" / "AI-Engineering")
    return {
        "repository_root": repository_root,
        "repository": "magixhot/AI-Engineering",
        "control_issue": 130,
        "server_url": "http://127.0.0.1:4096",
    }


def test_build_service_config_accepts_strict_runtime_binding() -> None:
    config = build_service_config(valid_mapping())

    assert config.repository_root.is_absolute()
    assert config.repository == "magixhot/AI-Engineering"
    assert config.control_issue == 130
    assert config.server_url == "http://127.0.0.1:4096"
    assert config.poll_seconds == DEFAULT_POLL_SECONDS


def test_build_service_config_accepts_bounded_poll_override() -> None:
    mapping = valid_mapping()
    mapping["poll_seconds"] = 2.5

    config = build_service_config(mapping)

    assert config.poll_seconds == 2.5


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("repository_root", "relative/project"),
        ("repository", "not-a-repository"),
        ("control_issue", 0),
        ("control_issue", True),
        ("server_url", "https://127.0.0.1:4096"),
        ("server_url", "http://example.com:4096"),
        ("server_url", "http://127.0.0.1"),
        ("server_url", "http://127.0.0.1:not-a-port"),
        ("poll_seconds", 0.5),
        ("poll_seconds", 301),
        ("poll_seconds", True),
    ],
)
def test_build_service_config_fails_closed_for_invalid_values(
    key: str,
    value: object,
) -> None:
    mapping = valid_mapping()
    mapping[key] = value

    with pytest.raises(ServiceConfigError):
        build_service_config(mapping)


def test_build_service_config_rejects_unknown_keys() -> None:
    mapping = valid_mapping()
    mapping["token"] = "must-never-be-configured-here"

    with pytest.raises(ServiceConfigError, match="unknown configuration keys"):
        build_service_config(mapping)


def test_build_service_config_rejects_missing_required_keys() -> None:
    mapping = valid_mapping()
    del mapping["control_issue"]

    with pytest.raises(ServiceConfigError, match="missing configuration keys"):
        build_service_config(mapping)


def test_parse_service_config_rejects_duplicate_json_keys() -> None:
    raw = (
        '{"repository_root":"/workspace/AI-Engineering",'
        '"repository":"magixhot/AI-Engineering",'
        '"control_issue":130,"control_issue":131,'
        '"server_url":"http://127.0.0.1:4096"}'
    )

    with pytest.raises(ServiceConfigError, match="duplicate configuration key"):
        parse_service_config(raw)


def test_parse_service_config_rejects_non_object_root() -> None:
    with pytest.raises(ServiceConfigError, match="JSON object"):
        parse_service_config("[]")


def test_load_service_config_reads_utf8_json(tmp_path: Path) -> None:
    repository_root = str((tmp_path / "AI-Engineering").resolve())
    config_path = tmp_path / "service.json"
    config_path.write_text(
        '{"repository_root":'
        + repr(repository_root).replace("'", '"')
        + ',"repository":"magixhot/AI-Engineering",'
        '"control_issue":130,'
        '"server_url":"http://localhost:4096",'
        '"poll_seconds":5}',
        encoding="utf-8",
    )

    config = load_service_config(config_path)

    assert config.server_url == "http://localhost:4096"
    assert config.poll_seconds == 5.0


def test_load_service_config_does_not_expand_environment_or_home(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "service.json"
    config_path.write_text(
        '{"repository_root":"~/AI-Engineering",'
        '"repository":"magixhot/AI-Engineering",'
        '"control_issue":130,'
        '"server_url":"http://127.0.0.1:4096"}',
        encoding="utf-8",
    )

    with pytest.raises(ServiceConfigError, match="absolute path"):
        load_service_config(config_path)
