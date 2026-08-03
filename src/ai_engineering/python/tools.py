"""
Python development MCP tools.
"""

from __future__ import annotations

from pathlib import Path

from .service import PythonService

_service = PythonService()


def python_version() -> dict:
    """
    Return Python runtime information.
    """
    result = _service.version()

    return {
        "executable": result.executable,
        "version": result.version,
    }


def python_run_tests(path: str | None = None) -> dict:
    """
    Run pytest.
    """
    result = _service.run_tests(
        Path(path) if path else None
    )

    return {
        "command": result.command,
        "success": result.success,
        "exit_code": result.exit_code,
        "output": result.output,
    }


def python_check_syntax(file: str) -> dict:
    """
    Check Python file syntax.
    """
    result = _service.check_syntax(
        Path(file)
    )

    return {
        "file": result.file,
        "valid": result.valid,
        "error": result.error,
    }


def python_inspect_package(path: str) -> dict:
    """
    Inspect Python package modules.
    """
    return {
        "path": path,
        "modules": _service.inspect_package(
            Path(path)
        ),
    }