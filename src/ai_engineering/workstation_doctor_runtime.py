"""Read-only workstation discovery/runtime for AUTO-0016."""

from __future__ import annotations

import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence
from urllib.error import URLError
from urllib.request import urlopen

from .opencode_service_config import ServiceConfigError, load_service_config
from .workstation_doctor_model import (
    CANONICAL_WORKER_UNIT,
    CheckState,
    WorkstationCheck,
    WorkstationCheckResult,
    WorkstationDoctorReport,
    build_check_result,
    build_doctor_report,
)

EXPECTED_REPOSITORY = "magixhot/AI-Engineering"
EXPECTED_BRANCH = "master"
EXPECTED_CONTROL_ISSUE = 130
COMMAND_TIMEOUT_SECONDS = 5.0
HEALTH_TIMEOUT_SECONDS = 2.0


@dataclass(frozen=True, slots=True)
class CommandObservation:
    returncode: int
    stdout: str = ""
    stderr: str = ""


CommandRunner = Callable[[Sequence[str]], CommandObservation]
HealthProbe = Callable[[str], bool]


def _real_command_runner(command: Sequence[str]) -> CommandObservation:
    try:
        completed = subprocess.run(
            list(command),
            capture_output=True,
            check=False,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return CommandObservation(returncode=127)
    return CommandObservation(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _real_health_probe(server_url: str) -> bool:
    try:
        with urlopen(
            f"{server_url.rstrip('/')}/global/health",
            timeout=HEALTH_TIMEOUT_SECONDS,
        ) as response:
            return 200 <= int(response.status) < 300
    except (OSError, URLError, ValueError):
        return False


def _result(
    check: WorkstationCheck,
    state: CheckState,
    summary: str,
) -> WorkstationCheckResult:
    return build_check_result(check=check, state=state, summary=summary)


def _run_ok(runner: CommandRunner, command: Sequence[str]) -> CommandObservation:
    return runner(command)


def _normalize_remote(remote: str) -> str | None:
    value = remote.strip()
    https_prefix = "https://github.com/"
    ssh_prefix = "git@github.com:"
    if value.startswith(https_prefix):
        tail = value[len(https_prefix) :]
    elif value.startswith(ssh_prefix):
        tail = value[len(ssh_prefix) :]
    else:
        return None
    return tail.removesuffix(".git")


def _discover_repository(
    root: Path,
    runner: CommandRunner,
) -> WorkstationCheckResult:
    commands = {
        "top": ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        "branch": ["git", "-C", str(root), "branch", "--show-current"],
        "head": ["git", "-C", str(root), "rev-parse", "HEAD"],
        "remote": ["git", "-C", str(root), "remote", "get-url", "origin"],
        "status": ["git", "-C", str(root), "status", "--porcelain"],
    }
    observed = {name: _run_ok(runner, cmd) for name, cmd in commands.items()}
    if any(item.returncode != 0 for item in observed.values()):
        return _result(
            WorkstationCheck.REPOSITORY,
            CheckState.FAIL,
            "REPOSITORY_MISSING or repository evidence unavailable",
        )

    repository_root = observed["top"].stdout.strip()
    branch = observed["branch"].stdout.strip()
    head = observed["head"].stdout.strip()
    remote = _normalize_remote(observed["remote"].stdout)
    clean = not observed["status"].stdout.strip()

    drift: list[str] = []
    if remote != EXPECTED_REPOSITORY:
        drift.append("REPOSITORY_IDENTITY_DRIFT")
    if branch != EXPECTED_BRANCH:
        drift.append("BRANCH_DRIFT")
    if not clean:
        drift.append("WORKTREE_DIRTY")
    if drift:
        return _result(
            WorkstationCheck.REPOSITORY,
            CheckState.FAIL,
            ";".join(drift)
            + f" repository_root={repository_root} current_head={head}",
        )
    return _result(
        WorkstationCheck.REPOSITORY,
        CheckState.PASS,
        f"repository_root={repository_root} current_head={head} "
        "branch=master clean=true",
    )


def _extract_config_path(unit_text: str) -> Path | None:
    exec_start = None
    for raw_line in unit_text.splitlines():
        line = raw_line.strip()
        if line.startswith("ExecStart="):
            exec_start = line.removeprefix("ExecStart=")
    if exec_start is None:
        return None
    try:
        parts = shlex.split(exec_start)
    except ValueError:
        return None
    try:
        index = parts.index("--config")
        value = parts[index + 1]
    except (ValueError, IndexError):
        return None
    path = Path(value)
    return path if path.is_absolute() else None


def _discover_unit(
    runner: CommandRunner,
) -> tuple[WorkstationCheckResult, Path | None]:
    observation = _run_ok(
        runner,
        ["systemctl", "--user", "cat", CANONICAL_WORKER_UNIT, "--no-pager"],
    )
    if observation.returncode != 0:
        return (
            _result(
                WorkstationCheck.WORKER_UNIT,
                CheckState.FAIL,
                f"SERVICE_UNIT_MISSING service_unit={CANONICAL_WORKER_UNIT}",
            ),
            None,
        )
    config_path = _extract_config_path(observation.stdout)
    if config_path is None:
        return (
            _result(
                WorkstationCheck.WORKER_UNIT,
                CheckState.FAIL,
                f"SERVICE_UNIT_DRIFT service_unit={CANONICAL_WORKER_UNIT}",
            ),
            None,
        )
    return (
        _result(
            WorkstationCheck.WORKER_UNIT,
            CheckState.PASS,
            f"service_unit={CANONICAL_WORKER_UNIT} config_file={config_path}",
        ),
        config_path,
    )


def probe_workstation(
    repository_root: Path,
    *,
    command_runner: CommandRunner = _real_command_runner,
    health_probe: HealthProbe = _real_health_probe,
) -> WorkstationDoctorReport:
    """Inspect one workstation without modifying repository or service state."""

    checks: list[WorkstationCheckResult] = []

    linux = sys.platform.startswith("linux")
    checks.append(
        _result(
            WorkstationCheck.WSL_LINUX,
            CheckState.PASS if linux else CheckState.FAIL,
            "linux environment detected" if linux else "linux environment unavailable",
        )
    )

    systemd = _run_ok(command_runner, ["systemctl", "--user", "show-environment"])
    checks.append(
        _result(
            WorkstationCheck.SYSTEMD_USER,
            CheckState.PASS if systemd.returncode == 0 else CheckState.FAIL,
            "systemd user manager reachable"
            if systemd.returncode == 0
            else "systemd user manager unavailable",
        )
    )

    git = _run_ok(command_runner, ["git", "--version"])
    checks.append(
        _result(
            WorkstationCheck.GIT,
            CheckState.PASS if git.returncode == 0 else CheckState.FAIL,
            "git available" if git.returncode == 0 else "git unavailable",
        )
    )

    python_ok = sys.version_info >= (3, 11)
    checks.append(
        _result(
            WorkstationCheck.PYTHON,
            CheckState.PASS if python_ok else CheckState.FAIL,
            f"python={sys.version_info.major}.{sys.version_info.minor}",
        )
    )

    gh = _run_ok(command_runner, ["gh", "--version"])
    checks.append(
        _result(
            WorkstationCheck.GITHUB_CLI,
            CheckState.PASS if gh.returncode == 0 else CheckState.FAIL,
            "github cli available" if gh.returncode == 0 else "github cli unavailable",
        )
    )

    auth = _run_ok(command_runner, ["gh", "auth", "status"])
    checks.append(
        _result(
            WorkstationCheck.GITHUB_AUTH,
            CheckState.PASS if auth.returncode == 0 else CheckState.FAIL,
            "github authentication present"
            if auth.returncode == 0
            else "GITHUB_AUTH_UNAVAILABLE",
        )
    )

    checks.append(_discover_repository(repository_root, command_runner))
    unit_result, config_path = _discover_unit(command_runner)
    checks.append(unit_result)

    config = None
    if config_path is None:
        checks.append(
            _result(
                WorkstationCheck.WORKER_CONFIG,
                CheckState.FAIL,
                "CONFIG_MISSING",
            )
        )
    else:
        try:
            config = load_service_config(config_path)
        except ServiceConfigError:
            checks.append(
                _result(
                    WorkstationCheck.WORKER_CONFIG,
                    CheckState.FAIL,
                    f"CONFIG_INVALID config_file={config_path}",
                )
            )
        else:
            state = (
                CheckState.PASS
                if config.repository == EXPECTED_REPOSITORY
                and config.control_issue == EXPECTED_CONTROL_ISSUE
                else CheckState.FAIL
            )
            summary = (
                f"config_file={config_path} repository_root={config.repository_root}"
                if state is CheckState.PASS
                else f"CONFIG_INVALID config_file={config_path}"
            )
            checks.append(_result(WorkstationCheck.WORKER_CONFIG, state, summary))

    if config is None:
        checks.append(
            _result(
                WorkstationCheck.OPENCODE_LOOPBACK,
                CheckState.UNKNOWN,
                "OpenCode endpoint unavailable until worker config is valid",
            )
        )
    else:
        healthy = health_probe(config.server_url)
        checks.append(
            _result(
                WorkstationCheck.OPENCODE_LOOPBACK,
                CheckState.PASS if healthy else CheckState.FAIL,
                "OpenCode loopback healthy" if healthy else "OPENCODE_UNAVAILABLE",
            )
        )

    active = _run_ok(
        command_runner,
        ["systemctl", "--user", "is-active", CANONICAL_WORKER_UNIT],
    )
    service_active = active.returncode == 0 and active.stdout.strip() == "active"
    checks.append(
        _result(
            WorkstationCheck.WORKER_ACTIVE,
            CheckState.PASS if service_active else CheckState.FAIL,
            "service_active=true" if service_active else "SERVICE_INACTIVE",
        )
    )

    channel = _run_ok(
        command_runner,
        [
            "gh",
            "api",
            f"repos/{EXPECTED_REPOSITORY}/issues/{EXPECTED_CONTROL_ISSUE}",
            "--jq",
            ".number",
        ],
    )
    checks.append(
        _result(
            WorkstationCheck.CONTROL_CHANNEL,
            CheckState.PASS if channel.returncode == 0 else CheckState.FAIL,
            "control issue reachable"
            if channel.returncode == 0
            else "QUALITY_RELAY_UNAVAILABLE",
        )
    )

    return build_doctor_report(tuple(checks))


def render_doctor_report(report: WorkstationDoctorReport) -> str:
    """Render bounded local-only diagnostic output."""

    lines = [f"workstation_readiness={report.readiness.value}"]
    lines.extend(
        f"{result.check.value}={result.state.value} {result.summary}"
        for result in report.checks
    )
    return "\n".join(lines)
