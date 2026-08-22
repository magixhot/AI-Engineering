from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VERSION = "0.3.0"
EXPECTED_ENTRY_POINT = "ai-engineering = ai_engineering.public_cli:main"
INFRA_MODULES = (
    "ai_engineering/local_agent_routing.py",
    "ai_engineering/local_agent_shadow.py",
)


def _environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    return environment


def _run(command: list[str], *, cwd: Path, environment: dict[str, str]) -> str:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _venv_executable(venv_directory: Path, name: str) -> Path:
    scripts = venv_directory / ("Scripts" if os.name == "nt" else "bin")
    suffix = ".exe" if os.name == "nt" and name in {"python", "ai-engineering"} else ""
    return scripts / f"{name}{suffix}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_rel_0004_distribution_boundary_and_installed_mcp(tmp_path: Path) -> None:
    environment = _environment()
    dist = tmp_path / "dist"
    isolated = tmp_path / "isolated"
    dist.mkdir()
    isolated.mkdir()

    _run(
        [sys.executable, "-m", "build", "--outdir", str(dist)],
        cwd=PROJECT_ROOT,
        environment=environment,
    )

    wheel = next(dist.glob(f"ai_engineering-{EXPECTED_VERSION}-*.whl"))
    sdist = dist / f"ai_engineering-{EXPECTED_VERSION}.tar.gz"
    assert sdist.is_file()

    dist_info = f"ai_engineering-{EXPECTED_VERSION}.dist-info"
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        for module in INFRA_MODULES:
            assert module in names
        entry_points = archive.read(f"{dist_info}/entry_points.txt").decode("utf-8")
        console_lines = [
            line.strip()
            for line in entry_points.splitlines()
            if line.strip() and not line.startswith("[")
        ]
        assert console_lines == [EXPECTED_ENTRY_POINT]

    with tarfile.open(sdist) as archive:
        names = set(archive.getnames())
        root = f"ai_engineering-{EXPECTED_VERSION}/src/"
        for module in INFRA_MODULES:
            assert f"{root}{module}" in names

    venv_directory = tmp_path / "venv"
    venv.create(venv_directory, with_pip=True)
    python = _venv_executable(venv_directory, "python")
    cli = _venv_executable(venv_directory, "ai-engineering")
    _run(
        [str(python), "-m", "pip", "install", str(wheel)],
        cwd=isolated,
        environment=environment,
    )

    installed = json.loads(
        _run(
            [
                str(python),
                "-c",
                (
                    "import importlib.metadata as m, json; "
                    "eps=[(e.name,e.value) for e in m.entry_points(group='console_scripts') "
                    "if e.dist and e.dist.name=='ai-engineering']; "
                    "print(json.dumps({'version':m.version('ai-engineering'),'eps':eps}))"
                ),
            ],
            cwd=isolated,
            environment=environment,
        )
    )
    assert installed == {
        "version": EXPECTED_VERSION,
        "eps": [["ai-engineering", "ai_engineering.public_cli:main"]],
    }

    top_help = _run([str(cli), "--help"], cwd=isolated, environment=environment)
    reconcile_help = _run(
        [str(cli), "project", "reconcile", "--help"],
        cwd=isolated,
        environment=environment,
    )
    workstation_help = _run(
        [str(cli), "workstation", "--help"],
        cwd=isolated,
        environment=environment,
    )
    assert "workstation" in top_help
    assert "approve" in reconcile_help
    assert "run" in reconcile_help
    assert "doctor" in workstation_help

    protocol_version = _run(
        [
            str(python),
            "-c",
            "from mcp.types import LATEST_PROTOCOL_VERSION; print(LATEST_PROTOCOL_VERSION)",
        ],
        cwd=isolated,
        environment=environment,
    ).strip()
    request_id = "rel-0004-installed-initialize"
    initialize = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "initialize",
        "params": {
            "protocolVersion": protocol_version,
            "capabilities": {},
            "clientInfo": {"name": "rel-0004-readiness", "version": "1.0.0"},
        },
    }
    initialized = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    process = subprocess.run(
        [str(python), "-m", "ai_engineering.stdio"],
        cwd=isolated,
        env=environment,
        input=(json.dumps(initialize) + "\n" + json.dumps(initialized) + "\n"),
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )
    responses = [json.loads(line) for line in process.stdout.splitlines() if line.strip()]
    response = next(item for item in responses if item.get("id") == request_id)
    assert "error" not in response
    assert response["result"]["serverInfo"] == {
        "name": "AI-Engineering",
        "version": EXPECTED_VERSION,
    }

    print(f"REL0004_WHEEL={wheel.name}")
    print(f"REL0004_WHEEL_SHA256={_sha256(wheel)}")
    print(f"REL0004_SDIST={sdist.name}")
    print(f"REL0004_SDIST_SHA256={_sha256(sdist)}")
    print("REL0004_INSTALLED_MCP=PASS")
    print("REL0004_INFRA_DISTRIBUTION_BOUNDARY=PASS")
