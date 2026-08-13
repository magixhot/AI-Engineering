from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from ai_engineering.mcp import bootstrap
from ai_engineering.mcp.debug import config, logger, streams


def _reset_runtime_logger() -> None:
    runtime_logger = logger._runtime_logger
    if runtime_logger is None:
        return

    for handler in runtime_logger.handlers[:]:
        runtime_logger.removeHandler(handler)
        handler.close()

    logger._runtime_logger = None


@pytest.fixture(autouse=True)
def reset_diagnostics_state() -> None:
    """Keep the module-level diagnostics logger isolated between tests."""

    _reset_runtime_logger()
    yield
    _reset_runtime_logger()


def test_diagnostics_are_disabled_by_default_without_stdio_wrapping(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AI_ENGINEERING_DEBUG_MCP", raising=False)
    stdin = object()
    stdout = object()

    assert config.is_debug_enabled() is False
    assert config.get_logs_dir() == Path("logs")
    assert not (tmp_path / "logs").exists()
    assert logger.get_runtime_logger() is None
    assert streams.wrap_stdio(stdin, stdout) == (stdin, stdout)
    assert not (tmp_path / "logs").exists()

    bootstrap_source = inspect.getsource(bootstrap)
    assert "wrap_stdio" not in bootstrap_source
    assert "stdio_server" in bootstrap_source


def test_enabled_diagnostics_write_runtime_events_outside_protocol_streams(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AI_ENGINEERING_DEBUG_MCP", "1")

    runtime_logger = logger.get_runtime_logger()

    assert runtime_logger is not None
    assert runtime_logger.name == "ai_engineering.mcp.diagnostics.runtime"
    assert (tmp_path / "logs" / "mcp-runtime.log").is_file()

    runtime_logger.info("diagnostics contract runtime event")
    for handler in runtime_logger.handlers:
        handler.flush()

    log_contents = (tmp_path / "logs" / "mcp-runtime.log").read_text(
        encoding="utf-8"
    )
    assert "diagnostics contract runtime event" in log_contents
    assert capsys.readouterr() == ("", "")
