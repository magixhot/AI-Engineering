"""Typed local runtime/service configuration for AUTO-0014."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

DEFAULT_REPOSITORY = "magixhot/AI-Engineering"
DEFAULT_CONTROL_ISSUE = 130
DEFAULT_SERVER_URL = "http://127.0.0.1:4096"
DEFAULT_POLL_SECONDS = 10.0
MIN_POLL_SECONDS = 1.0
MAX_POLL_SECONDS = 300.0

_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_ALLOWED_HOSTS = {"127.0.0.1", "localhost", "::1"}
_REQUIRED_KEYS = {
    "repository_root",
    "repository",
    "control_issue",
    "server_url",
}
_OPTIONAL_KEYS = {"poll_seconds"}


class ServiceConfigError(ValueError):
    """Raised when AUTO-0014 runtime configuration fails closed."""


@dataclass(frozen=True, slots=True)
class ServiceRuntimeConfig:
    """Validated local runtime binding for one AUTO-0013 worker instance."""

    repository_root: Path
    repository: str
    control_issue: int
    server_url: str
    poll_seconds: float = DEFAULT_POLL_SECONDS


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ServiceConfigError(f"duplicate configuration key: {key}")
        result[key] = value
    return result


def _validate_repository_root(value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise ServiceConfigError("repository_root must be a non-empty string")
    if any(char in value for char in ("\n", "\r", "\x00")):
        raise ServiceConfigError("repository_root contains forbidden characters")
    path = Path(value)
    if not path.is_absolute():
        raise ServiceConfigError("repository_root must be an absolute path")
    return path


def _validate_repository(value: Any) -> str:
    if not isinstance(value, str) or _REPOSITORY_RE.fullmatch(value) is None:
        raise ServiceConfigError("repository must use owner/name form")
    return value


def _validate_control_issue(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ServiceConfigError("control_issue must be a positive integer")
    return value


def _validate_server_url(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise ServiceConfigError("server_url must be a non-empty string")
    try:
        parsed = urlparse(value)
        port = parsed.port
    except ValueError as exc:
        raise ServiceConfigError("server_url has an invalid port") from exc
    if parsed.scheme != "http":
        raise ServiceConfigError("server_url must use local HTTP")
    if parsed.hostname not in _ALLOWED_HOSTS:
        raise ServiceConfigError("server_url must use a loopback host")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ServiceConfigError("server_url contains forbidden fields")
    if parsed.path not in {"", "/"}:
        raise ServiceConfigError("server_url must not contain a path")
    if port is None:
        raise ServiceConfigError("server_url must include an explicit port")
    return value.rstrip("/")


def _validate_poll_seconds(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ServiceConfigError("poll_seconds must be numeric")
    result = float(value)
    if result < MIN_POLL_SECONDS or result > MAX_POLL_SECONDS:
        raise ServiceConfigError(
            f"poll_seconds must be between {MIN_POLL_SECONDS:g} and "
            f"{MAX_POLL_SECONDS:g}"
        )
    return result


def build_service_config(mapping: Mapping[str, Any]) -> ServiceRuntimeConfig:
    """Build one strict runtime configuration from an already-decoded object."""

    keys = set(mapping)
    unknown = keys - _REQUIRED_KEYS - _OPTIONAL_KEYS
    missing = _REQUIRED_KEYS - keys
    if unknown:
        raise ServiceConfigError(
            "unknown configuration keys: " + ", ".join(sorted(unknown))
        )
    if missing:
        raise ServiceConfigError(
            "missing configuration keys: " + ", ".join(sorted(missing))
        )

    return ServiceRuntimeConfig(
        repository_root=_validate_repository_root(mapping["repository_root"]),
        repository=_validate_repository(mapping["repository"]),
        control_issue=_validate_control_issue(mapping["control_issue"]),
        server_url=_validate_server_url(mapping["server_url"]),
        poll_seconds=_validate_poll_seconds(
            mapping.get("poll_seconds", DEFAULT_POLL_SECONDS)
        ),
    )


def parse_service_config(data: str | bytes) -> ServiceRuntimeConfig:
    """Parse strict UTF-8 JSON configuration with duplicate-key rejection."""

    if isinstance(data, bytes):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ServiceConfigError("configuration must be UTF-8 JSON") from exc
    elif isinstance(data, str):
        text = data
    else:
        raise ServiceConfigError("configuration must be text or bytes")

    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except json.JSONDecodeError as exc:
        raise ServiceConfigError("configuration is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ServiceConfigError("configuration root must be a JSON object")
    return build_service_config(value)


def load_service_config(path: Path) -> ServiceRuntimeConfig:
    """Load one local runtime configuration file without environment expansion."""

    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ServiceConfigError("configuration file could not be read") from exc
    return parse_service_config(data)
