from __future__ import annotations

import tomllib
from pathlib import Path

from ai_engineering import public_cli
from ai_engineering.mcp.config import MCPConfig
from ai_engineering.version import VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_release_version_contract_is_0_3_0() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    lock = (ROOT / "uv.lock").read_text(encoding="utf-8")

    assert VERSION == "0.3.0"
    assert pyproject["project"]["version"] == VERSION
    assert MCPConfig().server_version == VERSION
    assert (
        'name = "ai-engineering"\nversion = "0.3.0"\nsource = { editable = "." }'
        in lock
    )


def test_sdk_adapter_has_no_stale_server_version_literal() -> None:
    source = (ROOT / "src/ai_engineering/mcp/sdk_adapter.py").read_text(
        encoding="utf-8"
    )
    server_source = (ROOT / "src/ai_engineering/mcp/server.py").read_text(
        encoding="utf-8"
    )

    assert 'version="0.1.0"' not in source
    assert "version=version" in source
    assert "version=self._config.server_version" in server_source


def test_public_top_level_help_exposes_workstation(capsys) -> None:
    assert public_cli.main(["--help"]) == 0
    output = capsys.readouterr().out
    assert "project" in output
    assert "workstation" in output


def test_public_reconcile_help_exposes_all_actions(capsys) -> None:
    assert public_cli.main(["project", "reconcile", "--help"]) == 0
    output = capsys.readouterr().out
    for action in ("plan", "apply", "approve", "run"):
        assert action in output


def test_public_workstation_help_exposes_doctor(capsys) -> None:
    assert public_cli.main(["workstation", "--help"]) == 0
    output = capsys.readouterr().out
    assert "doctor" in output
