"""Typed read-only workstation doctor model for AUTO-0016."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

CANONICAL_WORKER_UNIT = "ai-engineering-worker.service"


class WorkstationDoctorError(ValueError):
    """Raised when workstation doctor evidence violates the typed contract."""


class CheckState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class WorkstationReadiness(str, Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"


class WorkstationCheck(str, Enum):
    WSL_LINUX = "wsl_linux"
    SYSTEMD_USER = "systemd_user"
    GIT = "git"
    PYTHON = "python"
    GITHUB_CLI = "github_cli"
    GITHUB_AUTH = "github_auth"
    REPOSITORY = "repository"
    OPENCODE_LOOPBACK = "opencode_loopback"
    WORKER_CONFIG = "worker_config"
    WORKER_UNIT = "worker_unit"
    WORKER_ACTIVE = "worker_active"
    CONTROL_CHANNEL = "control_channel"


REQUIRED_CHECKS = tuple(WorkstationCheck)


@dataclass(frozen=True, slots=True)
class WorkstationCheckResult:
    check: WorkstationCheck
    state: CheckState
    summary: str


@dataclass(frozen=True, slots=True)
class WorkstationDoctorReport:
    checks: tuple[WorkstationCheckResult, ...]
    readiness: WorkstationReadiness

    @property
    def ready(self) -> bool:
        return self.readiness is WorkstationReadiness.READY


def _validate_summary(summary: str) -> None:
    if not isinstance(summary, str) or not summary.strip():
        raise WorkstationDoctorError("summary must be a non-empty string")
    if "\n" in summary or "\r" in summary:
        raise WorkstationDoctorError("summary must be single-line")


def build_check_result(
    *,
    check: WorkstationCheck,
    state: CheckState,
    summary: str,
) -> WorkstationCheckResult:
    if not isinstance(check, WorkstationCheck):
        raise WorkstationDoctorError("check must be a WorkstationCheck")
    if not isinstance(state, CheckState):
        raise WorkstationDoctorError("state must be a CheckState")
    _validate_summary(summary)
    return WorkstationCheckResult(check=check, state=state, summary=summary.strip())


def build_doctor_report(
    checks: tuple[WorkstationCheckResult, ...],
) -> WorkstationDoctorReport:
    if not checks:
        raise WorkstationDoctorError("checks must not be empty")

    seen: set[WorkstationCheck] = set()
    for result in checks:
        if not isinstance(result, WorkstationCheckResult):
            raise WorkstationDoctorError("checks must contain typed check results")
        if result.check in seen:
            raise WorkstationDoctorError("duplicate workstation doctor check")
        seen.add(result.check)
        _validate_summary(result.summary)

    missing = set(REQUIRED_CHECKS) - seen
    extra = seen - set(REQUIRED_CHECKS)
    if missing or extra:
        raise WorkstationDoctorError(
            "doctor report must contain every required check once"
        )

    readiness = (
        WorkstationReadiness.READY
        if all(result.state is CheckState.PASS for result in checks)
        else WorkstationReadiness.NOT_READY
    )
    return WorkstationDoctorReport(checks=checks, readiness=readiness)
