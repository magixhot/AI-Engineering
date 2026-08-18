from __future__ import annotations

from pathlib import Path

import pytest

from ai_engineering.opencode_user_service import (
    UserServiceError,
    UserServicePaths,
    render_systemd_user_unit,
    validate_user_service_paths,
    write_user_service_unit,
)


def make_paths(tmp_path: Path) -> UserServicePaths:
    return UserServicePaths(
        unit_path=(tmp_path / "systemd" / "ai-engineering-worker.service").resolve(),
        config_path=(tmp_path / "config" / "worker.json").resolve(),
        runtime_dir=(tmp_path / "runtime").resolve(),
    )


def test_validate_user_service_paths_requires_absolute_paths(tmp_path: Path) -> None:
    paths = UserServicePaths(
        unit_path=Path("worker.service"),
        config_path=(tmp_path / "worker.json").resolve(),
        runtime_dir=(tmp_path / "runtime").resolve(),
    )

    with pytest.raises(UserServiceError, match="unit_path must be an absolute path"):
        validate_user_service_paths(paths)


def test_validate_user_service_paths_requires_service_suffix(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    invalid = UserServicePaths(
        unit_path=paths.unit_path.with_suffix(".txt"),
        config_path=paths.config_path,
        runtime_dir=paths.runtime_dir,
    )

    with pytest.raises(UserServiceError, match="unit_path must name a .service file"):
        validate_user_service_paths(invalid)


def test_render_systemd_user_unit_is_user_scoped_and_bounded(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    python_executable = Path("/usr/bin/python3")

    unit = render_systemd_user_unit(
        python_executable=python_executable,
        paths=paths,
    )

    assert "python3 -m ai_engineering.opencode_worker_lifecycle" in unit
    assert f"--config {paths.config_path}" in unit
    assert f"--runtime-dir {paths.runtime_dir}" in unit
    assert "Restart=on-failure" in unit
    assert "RestartSec=5s" in unit
    assert "NoNewPrivileges=yes" in unit
    assert "ProtectSystem=strict" in unit
    assert "ProtectHome=read-only" in unit
    assert "systemctl" not in unit
    assert "sudo" not in unit


def test_render_rejects_relative_python_executable(tmp_path: Path) -> None:
    with pytest.raises(UserServiceError, match="python_executable must be an absolute path"):
        render_systemd_user_unit(
            python_executable=Path("python3"),
            paths=make_paths(tmp_path),
        )


def test_write_user_service_unit_is_explicit_local_file_write(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    written = write_user_service_unit(
        python_executable=Path("/usr/bin/python3"),
        paths=paths,
    )

    assert written == paths.unit_path
    assert written.exists()
    text = written.read_text(encoding="utf-8")
    assert "ai_engineering.opencode_worker_lifecycle" in text
    assert written.stat().st_mode & 0o777 == 0o600
    assert not paths.config_path.exists()
    assert not paths.runtime_dir.exists()
