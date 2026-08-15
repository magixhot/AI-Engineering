"""
Python development service.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

from .exceptions import (
    PythonExecutionError,
    PythonPermissionError,
    SyntaxValidationError,
)
from .models import (
    PythonVersion,
    SyntaxCheckResult,
    TestResult,
)


class PythonService:
    """Provides Python development operations."""

    def __init__(
        self,
        workspace_root: Path | None = None,
        *,
        bounded: bool = False,
        timeout: int = 30,
    ) -> None:
        self._bounded = bounded
        self._workspace_root = (
            workspace_root.resolve() if workspace_root is not None else None
        )
        self._timeout = timeout

    def _authorize_path(self, path: Path) -> Path:
        if not self._bounded:
            return path
        if self._workspace_root is None:
            raise PythonPermissionError("Python workspace root is not configured.")

        candidate = path
        if not candidate.is_absolute():
            candidate = self._workspace_root / candidate
        resolved = candidate.resolve()

        try:
            resolved.relative_to(self._workspace_root)
        except ValueError as exc:
            raise PythonPermissionError(
                "Path outside configured workspace root."
            ) from exc
        return resolved

    def version(self) -> PythonVersion:
        """Return current Python runtime information."""
        return PythonVersion(
            executable=sys.executable,
            version=sys.version.split()[0],
        )

    def run_tests(
        self,
        path: Path | None = None,
    ) -> TestResult:
        """Run pytest for a project."""

        target_display = str(path) if path else "tests"
        target_path = Path(target_display)
        authorized_target = self._authorize_path(target_path)
        subprocess_target = (
            str(authorized_target) if self._bounded else target_display
        )

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    subprocess_target,
                ],
                cwd=self._workspace_root if self._bounded else None,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                shell=False,
                timeout=self._timeout if self._bounded else None,
            )

        except subprocess.TimeoutExpired as exc:
            raise PythonExecutionError("Python test command timed out.") from exc
        except Exception as exc:
            raise PythonExecutionError(str(exc)) from exc

        return TestResult(
            command=f"pytest {target_display}",
            success=result.returncode == 0,
            exit_code=result.returncode,
            output=result.stdout + result.stderr,
        )

    def check_syntax(
        self,
        file: Path,
    ) -> SyntaxCheckResult:
        """Validate Python file syntax."""

        authorized_file = self._authorize_path(file)

        try:
            source = authorized_file.read_text(
                encoding="utf-8",
            )

            ast.parse(source)

        except SyntaxError as exc:
            return SyntaxCheckResult(
                file=str(file),
                valid=False,
                error=str(exc),
            )

        except Exception as exc:
            raise SyntaxValidationError(
                str(exc)
            ) from exc

        return SyntaxCheckResult(
            file=str(file),
            valid=True,
        )

    def inspect_package(
        self,
        path: Path,
    ) -> list[str]:
        """List Python modules in a package."""

        authorized_path = self._authorize_path(path)

        if not authorized_path.exists():
            raise PythonExecutionError(
                f"Package not found: {path}"
            )

        return sorted(
            item.name
            for item in authorized_path.glob("*.py")
        )