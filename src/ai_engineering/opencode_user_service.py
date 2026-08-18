"""Explicit user-scoped service integration helpers for AUTO-0014."""

from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from pathlib import Path


class UserServiceError(ValueError):
    """Raised when user-service integration fails closed."""


@dataclass(frozen=True, slots=True)
class UserServicePaths:
    """Explicit local destinations for AUTO-0014 service integration."""

    unit_path: Path
    config_path: Path
    runtime_dir: Path


def _require_absolute(path: Path, label: str) -> Path:
    if not path.is_absolute():
        raise UserServiceError(f"{label} must be an absolute path")
    return path


def validate_user_service_paths(paths: UserServicePaths) -> UserServicePaths:
    """Validate explicit local paths without environment or home expansion."""

    unit_path = _require_absolute(paths.unit_path, "unit_path")
    config_path = _require_absolute(paths.config_path, "config_path")
    runtime_dir = _require_absolute(paths.runtime_dir, "runtime_dir")
    if unit_path.suffix != ".service":
        raise UserServiceError("unit_path must name a .service file")
    if config_path == unit_path:
        raise UserServiceError("config_path and unit_path must differ")
    return UserServicePaths(
        unit_path=unit_path,
        config_path=config_path,
        runtime_dir=runtime_dir,
    )


def render_systemd_user_unit(
    *,
    python_executable: Path,
    paths: UserServicePaths,
) -> str:
    """Render a user-scoped systemd unit for the validated lifecycle entrypoint."""

    validated = validate_user_service_paths(paths)
    python_executable = _require_absolute(python_executable, "python_executable")

    command = " ".join(
        shlex.quote(str(part))
        for part in (
            python_executable,
            "-m",
            "ai_engineering.opencode_worker_lifecycle",
            "--config",
            validated.config_path,
            "--runtime-dir",
            validated.runtime_dir,
        )
    )
    return (
        "[Unit]\n"
        "Description=AI-Engineering read-only OpenCode control worker\n"
        "After=default.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"ExecStart={command}\n"
        "Restart=on-failure\n"
        "RestartSec=5s\n"
        "NoNewPrivileges=yes\n"
        "PrivateTmp=yes\n"
        "ProtectSystem=strict\n"
        "ProtectHome=read-only\n\n"
        "[Install]\n"
        "WantedBy=default.target\n"
    )


def write_user_service_unit(
    *,
    python_executable: Path,
    paths: UserServicePaths,
) -> Path:
    """Explicitly write one local user-service unit; never enable or start it."""

    validated = validate_user_service_paths(paths)
    content = render_systemd_user_unit(
        python_executable=python_executable,
        paths=validated,
    )
    try:
        validated.unit_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        validated.unit_path.write_text(content, encoding="utf-8")
        os.chmod(validated.unit_path, 0o600)
    except OSError as exc:
        raise UserServiceError("user service unit could not be written") from exc
    return validated.unit_path
