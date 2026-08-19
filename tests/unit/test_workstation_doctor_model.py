from __future__ import annotations

import pytest

from ai_engineering.workstation_doctor_model import (
    CANONICAL_WORKER_UNIT,
    REQUIRED_CHECKS,
    CheckState,
    WorkstationCheck,
    WorkstationDoctorError,
    WorkstationReadiness,
    build_check_result,
    build_doctor_report,
)


def _all(state: CheckState):
    return tuple(
        build_check_result(
            check=check,
            state=state,
            summary=f"{check.value} observed",
        )
        for check in REQUIRED_CHECKS
    )


def test_canonical_worker_unit_is_stable() -> None:
    assert CANONICAL_WORKER_UNIT == "ai-engineering-worker.service"


def test_ready_requires_every_check_to_pass() -> None:
    report = build_doctor_report(_all(CheckState.PASS))
    assert report.readiness is WorkstationReadiness.READY
    assert report.ready is True


def test_unknown_fails_closed() -> None:
    checks = list(_all(CheckState.PASS))
    checks[0] = build_check_result(
        check=WorkstationCheck.WSL_LINUX,
        state=CheckState.UNKNOWN,
        summary="environment could not be determined safely",
    )
    report = build_doctor_report(tuple(checks))
    assert report.readiness is WorkstationReadiness.NOT_READY
    assert report.ready is False


def test_missing_check_is_rejected() -> None:
    with pytest.raises(WorkstationDoctorError, match="every required check"):
        build_doctor_report(_all(CheckState.PASS)[:-1])


def test_duplicate_check_is_rejected() -> None:
    checks = _all(CheckState.PASS)
    with pytest.raises(WorkstationDoctorError, match="duplicate"):
        build_doctor_report(checks[:-1] + (checks[0],))


def test_summary_must_be_bounded_single_line() -> None:
    with pytest.raises(WorkstationDoctorError, match="single-line"):
        build_check_result(
            check=WorkstationCheck.GIT,
            state=CheckState.PASS,
            summary="git ok\nprivate detail",
        )
