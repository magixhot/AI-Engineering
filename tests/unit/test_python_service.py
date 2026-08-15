from __future__ import annotations

import sys
from pathlib import Path

import pytest

from ai_engineering.python.exceptions import (
    PythonExecutionError,
    SyntaxValidationError,
)
from ai_engineering.python.service import PythonService


def test_version_reports_the_current_interpreter() -> None:
    result = PythonService().version()

    assert result.executable == sys.executable
    assert result.version == sys.version.split()[0]


def test_check_syntax_reports_valid_and_invalid_fixture_files(tmp_path: Path) -> None:
    service = PythonService()
    valid_file = tmp_path / "valid.py"
    invalid_file = tmp_path / "invalid.py"
    valid_file.write_text("value = 1\n", encoding="utf-8")
    invalid_file.write_text("def broken(:\n", encoding="utf-8")

    valid = service.check_syntax(valid_file)
    invalid = service.check_syntax(invalid_file)

    assert valid.file == str(valid_file)
    assert valid.valid is True
    assert valid.error is None
    assert invalid.file == str(invalid_file)
    assert invalid.valid is False
    assert invalid.error is not None


def test_check_syntax_missing_file_preserves_domain_error(tmp_path: Path) -> None:
    with pytest.raises(SyntaxValidationError):
        PythonService().check_syntax(tmp_path / "missing.py")


def test_inspect_package_lists_sorted_modules_and_rejects_missing_path(
    tmp_path: Path,
) -> None:
    service = PythonService()
    package = tmp_path / "package"
    package.mkdir()
    (package / "zeta.py").write_text("", encoding="utf-8")
    (package / "alpha.py").write_text("", encoding="utf-8")
    (package / "ignored.txt").write_text("", encoding="utf-8")

    assert service.inspect_package(package) == ["alpha.py", "zeta.py"]
    with pytest.raises(PythonExecutionError, match="Package not found"):
        service.inspect_package(tmp_path / "missing-package")


def test_inspect_package_existing_file_preserves_current_empty_result(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "not-a-directory.py"
    file_path.write_text("", encoding="utf-8")

    assert PythonService().inspect_package(file_path) == []


def test_run_tests_reports_passing_and_failing_fixture_targets(tmp_path: Path) -> None:
    service = PythonService()
    passing_test = tmp_path / "test_passing.py"
    failing_test = tmp_path / "test_failing.py"
    passing_test.write_text("def test_passes():\n    assert True\n", encoding="utf-8")
    failing_test.write_text("def test_fails():\n    assert False\n", encoding="utf-8")

    passing = service.run_tests(passing_test)
    failing = service.run_tests(failing_test)

    assert passing.command == f"pytest {passing_test}"
    assert passing.success is True
    assert passing.exit_code == 0
    assert "1 passed" in passing.output
    assert failing.command == f"pytest {failing_test}"
    assert failing.success is False
    assert failing.exit_code != 0
    assert "1 failed" in failing.output
