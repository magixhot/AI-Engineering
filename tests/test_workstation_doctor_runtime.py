from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from ai_engineering.workstation_doctor_model import (
    CheckState,
    WorkstationCheck,
    WorkstationReadiness,
)
from ai_engineering.workstation_doctor_runtime import (
    CommandObservation,
    probe_workstation,
    render_doctor_report,
)


def _ready_runner(root: Path, config_path: Path):
    unit = (
        "[Service]\n"
        "ExecStart=/usr/bin/python3 -m ai_engineering.opencode_worker_lifecycle "
        f"--config {config_path} --runtime-dir /run/user/1000/ai-engineering-worker\n"
    )

    def run(command: Sequence[str]) -> CommandObservation:
        args = list(command)
        if args == ["systemctl", "--user", "show-environment"]:
            return CommandObservation(0, "HOME=/redacted\n")
        if args == ["git", "--version"]:
            return CommandObservation(0, "git version 2.50\n")
        if args == ["gh", "--version"]:
            return CommandObservation(0, "gh version 2.80\n")
        if args == ["gh", "auth", "status"]:
            return CommandObservation(0, "authenticated\n")
        if args[:3] == ["git", "-C", str(root)]:
            tail = args[3:]
            if tail == ["rev-parse", "--show-toplevel"]:
                return CommandObservation(0, f"{root}\n")
            if tail == ["branch", "--show-current"]:
                return CommandObservation(0, "master\n")
            if tail == ["rev-parse", "HEAD"]:
                return CommandObservation(0, "a" * 40 + "\n")
            if tail == ["remote", "get-url", "origin"]:
                return CommandObservation(
                    0, "https://github.com/magixhot/AI-Engineering.git\n"
                )
            if tail == ["status", "--porcelain"]:
                return CommandObservation(0, "")
        if args == [
            "systemctl",
            "--user",
            "cat",
            "ai-engineering-worker.service",
            "--no-pager",
        ]:
            return CommandObservation(0, unit)
        if args == [
            "systemctl",
            "--user",
            "is-active",
            "ai-engineering-worker.service",
        ]:
            return CommandObservation(0, "active\n")
        if args[:2] == ["gh", "api"]:
            return CommandObservation(0, "130\n")
        return CommandObservation(127)

    return run


def test_probe_workstation_ready_uses_discovered_config(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    config_path = tmp_path / "worker.json"
    config_path.write_text(
        json.dumps(
            {
                "repository_root": str(root),
                "repository": "magixhot/AI-Engineering",
                "control_issue": 130,
                "server_url": "http://127.0.0.1:4096",
                "poll_seconds": 10,
            }
        ),
        encoding="utf-8",
    )

    observed_urls: list[str] = []

    def health(url: str) -> bool:
        observed_urls.append(url)
        return True

    report = probe_workstation(
        root,
        command_runner=_ready_runner(root, config_path),
        health_probe=health,
    )

    assert report.readiness is WorkstationReadiness.READY
    assert all(result.state is CheckState.PASS for result in report.checks)
    assert observed_urls == ["http://127.0.0.1:4096"]
    rendered = render_doctor_report(report)
    assert f"repository_root={root}" in rendered
    assert f"config_file={config_path}" in rendered
    assert "service_unit=ai-engineering-worker.service" in rendered
    assert "current_head=" + "a" * 40 in rendered
    assert "service_active=true" in rendered


def test_probe_workstation_fails_closed_when_unit_is_missing(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    ready = _ready_runner(root, tmp_path / "unused.json")

    def runner(command: Sequence[str]) -> CommandObservation:
        args = list(command)
        if args == [
            "systemctl",
            "--user",
            "cat",
            "ai-engineering-worker.service",
            "--no-pager",
        ]:
            return CommandObservation(1, "", "Unit not found")
        return ready(command)

    report = probe_workstation(root, command_runner=runner, health_probe=lambda _: True)
    by_check = {result.check: result for result in report.checks}

    assert report.readiness is WorkstationReadiness.NOT_READY
    assert by_check[WorkstationCheck.WORKER_UNIT].state is CheckState.FAIL
    assert "SERVICE_UNIT_MISSING" in by_check[WorkstationCheck.WORKER_UNIT].summary
    assert by_check[WorkstationCheck.WORKER_CONFIG].state is CheckState.FAIL
    assert by_check[WorkstationCheck.OPENCODE_LOOPBACK].state is CheckState.UNKNOWN
