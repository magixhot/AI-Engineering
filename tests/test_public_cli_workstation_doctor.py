from __future__ import annotations

from pathlib import Path

from ai_engineering import public_cli
from ai_engineering.workstation_doctor_model import (
    CheckState,
    WorkstationCheck,
    build_check_result,
    build_doctor_report,
)


def _report(state: CheckState):
    return build_doctor_report(
        tuple(
            build_check_result(check=check, state=state, summary="observed")
            for check in WorkstationCheck
        )
    )


def test_workstation_doctor_cli_returns_zero_when_ready(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    observed: list[Path] = []

    def probe(root: Path):
        observed.append(root)
        return _report(CheckState.PASS)

    monkeypatch.setattr(public_cli, "probe_workstation", probe)
    rc = public_cli.main(
        ["workstation", "doctor", "--repository-root", str(tmp_path)]
    )

    assert rc == 0
    assert observed == [tmp_path.resolve()]
    assert "workstation_readiness=READY" in capsys.readouterr().out


def test_workstation_doctor_cli_returns_one_when_not_ready(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        public_cli,
        "probe_workstation",
        lambda root: _report(CheckState.FAIL),
    )
    rc = public_cli.main(
        ["workstation", "doctor", "--repository-root", str(tmp_path)]
    )

    assert rc == 1
