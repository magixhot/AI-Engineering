from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, BinaryIO

import pytest
from mcp.types import LATEST_PROTOCOL_VERSION

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROCESS_TIMEOUT_SECONDS = 10
TERMINATION_TIMEOUT_SECONDS = 3


class PipeCapture:
    """Capture a subprocess pipe without blocking the test thread."""

    def __init__(self, stream: BinaryIO) -> None:
        self.lines: list[bytes] = []
        self._lines: queue.Queue[bytes] = queue.Queue()
        self._thread = threading.Thread(target=self._read_lines, args=(stream,))

    def start(self) -> None:
        self._thread.start()

    def get_line(self, timeout: float) -> bytes:
        try:
            return self._lines.get(timeout=timeout)
        except queue.Empty:
            pytest.fail("Timed out waiting for MCP STDIO output.")

    def join(self) -> None:
        self._thread.join(timeout=TERMINATION_TIMEOUT_SECONDS)
        assert not self._thread.is_alive(), "Subprocess pipe reader did not stop."

    def _read_lines(self, stream: BinaryIO) -> None:
        for line in iter(stream.readline, b""):
            self.lines.append(line)
            self._lines.put(line)


def _server_environment() -> dict[str, str]:
    environment = os.environ.copy()
    source_path = str(REPOSITORY_ROOT / "src")
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = os.pathsep.join(
        path for path in (source_path, existing_pythonpath) if path
    )
    environment.pop("AI_ENGINEERING_DEBUG_MCP", None)
    return environment


def _parse_jsonrpc_line(line: bytes) -> dict[str, Any]:
    try:
        message = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        pytest.fail(f"stdout contained non-protocol output: {line!r} ({error})")

    assert isinstance(message, dict), "stdout JSON-RPC message must be an object."
    assert message.get("jsonrpc") == "2.0"
    return message


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return

    if process.stdin is not None and not process.stdin.closed:
        process.stdin.close()

    try:
        process.wait(timeout=TERMINATION_TIMEOUT_SECONDS)
        return
    except subprocess.TimeoutExpired:
        process.terminate()

    try:
        process.wait(timeout=TERMINATION_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=TERMINATION_TIMEOUT_SECONDS)


def test_stdio_initialize_is_protocol_only_and_exits_cleanly() -> None:
    """The module entry point accepts newline-delimited MCP JSON-RPC over STDIO."""

    process = subprocess.Popen(
        [sys.executable, "-m", "ai_engineering.stdio"],
        cwd=REPOSITORY_ROOT,
        env=_server_environment(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None

    stdout = PipeCapture(process.stdout)
    stderr = PipeCapture(process.stderr)
    stdout.start()
    stderr.start()

    request_id = "mcp-stdio-contract-initialize"
    initialize_request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "initialize",
        "params": {
            "protocolVersion": LATEST_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {
                "name": "mcp-stdio-contract-test",
                "version": "1.0.0",
            },
        },
    }

    try:
        process.stdin.write(json.dumps(initialize_request).encode("utf-8") + b"\n")
        process.stdin.flush()

        deadline = time.monotonic() + PROCESS_TIMEOUT_SECONDS
        response: dict[str, Any] | None = None
        while time.monotonic() < deadline:
            line = stdout.get_line(max(0.01, deadline - time.monotonic()))
            message = _parse_jsonrpc_line(line)
            if message.get("id") == request_id:
                response = message
                break

        assert response is not None, "Server did not return the initialize response."
        assert "error" not in response
        assert response["id"] == request_id

        result = response["result"]
        assert result["protocolVersion"] == LATEST_PROTOCOL_VERSION
        assert isinstance(result["capabilities"], dict)
        assert result["serverInfo"] == {
            "name": "AI-Engineering",
            "version": "0.1.0",
        }

        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        process.stdin.write(
            json.dumps(initialized_notification).encode("utf-8") + b"\n"
        )
        process.stdin.close()
        assert process.wait(timeout=PROCESS_TIMEOUT_SECONDS) == 0
    finally:
        _stop_process(process)
        stdout.join()
        stderr.join()

    stdout_messages = [_parse_jsonrpc_line(line) for line in stdout.lines]
    assert any(message.get("id") == request_id for message in stdout_messages)
