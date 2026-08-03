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
    SyntaxValidationError,
)
from .models import (
    PythonVersion,
    SyntaxCheckResult,
    TestResult,
)


class PythonService:
    """
    Provides Python development operations.
    """

    def version(self) -> PythonVersion:
        """
        Return current Python runtime information.
        """
        return PythonVersion(
            executable=sys.executable,
            version=sys.version.split()[0],
        )

    def run_tests(
        self,
        path: Path | None = None,
    ) -> TestResult:
        """
        Run pytest for a project.
        """

        target = str(path) if path else "tests"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    target,
                ],
                capture_output=True,
                text=True,
            )

        except Exception as exc:
            raise PythonExecutionError(
                str(exc)
            ) from exc

        return TestResult(
            command=f"pytest {target}",
            success=result.returncode == 0,
            exit_code=result.returncode,
            output=result.stdout + result.stderr,
        )

    def check_syntax(
        self,
        file: Path,
    ) -> SyntaxCheckResult:
        """
        Validate Python file syntax.
        """

        try:
            source = file.read_text(
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
        """
        List Python modules in a package.
        """

        if not path.exists():
            raise PythonExecutionError(
                f"Package not found: {path}"
            )

        return sorted(
            item.name
            for item in path.glob("*.py")
        )