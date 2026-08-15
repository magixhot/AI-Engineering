"""Python development MCP tools."""

from __future__ import annotations

from pathlib import Path

from .service import PythonService


class PythonTools:
    """Adapt a specific PythonService instance to MCP tool result shapes."""

    def __init__(self, service: PythonService) -> None:
        self._service = service

    def version(self) -> dict:
        result = self._service.version()
        return {
            "executable": result.executable,
            "version": result.version,
        }

    def run_tests(self, path: str | None = None) -> dict:
        result = self._service.run_tests(Path(path) if path else None)
        return {
            "command": result.command,
            "success": result.success,
            "exit_code": result.exit_code,
            "output": result.output,
        }

    def check_syntax(self, file: str) -> dict:
        result = self._service.check_syntax(Path(file))
        return {
            "file": result.file,
            "valid": result.valid,
            "error": result.error,
        }

    def inspect_package(self, path: str) -> dict:
        return {
            "path": path,
            "modules": self._service.inspect_package(Path(path)),
        }


_service = PythonService()
_tools = PythonTools(_service)


def python_version() -> dict:
    """Return Python runtime information."""
    return _tools.version()


def python_run_tests(path: str | None = None) -> dict:
    """Run pytest."""
    return _tools.run_tests(path)


def python_check_syntax(file: str) -> dict:
    """Check Python file syntax."""
    return _tools.check_syntax(file)


def python_inspect_package(path: str) -> dict:
    """Inspect Python package modules."""
    return _tools.inspect_package(path)
