from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request

from ai_engineering import opencode_readonly_adapter as adapter_module
from ai_engineering.opencode_readonly_adapter import OpenCodeHttpTransport


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def test_http_transport_routes_every_request_to_workspace(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: list[tuple[str, str | None]] = []

    def fake_urlopen(request: Request, *, timeout: float) -> FakeResponse:
        captured.append(
            (
                request.full_url,
                request.get_header("X-opencode-directory"),
            )
        )
        if request.full_url.endswith("/session"):
            return FakeResponse({"id": "session-1"})
        return FakeResponse({"parts": [{"type": "text", "text": "ok"}]})

    monkeypatch.setattr(adapter_module, "urlopen", fake_urlopen)
    transport = OpenCodeHttpTransport(directory=tmp_path)

    transport("/session", {"title": "test"})
    transport(
        "/session/session-1/message",
        {"parts": [{"type": "text", "text": "inspect"}]},
    )

    expected = str(tmp_path.resolve())
    assert captured == [
        ("http://127.0.0.1:4096/session", expected),
        ("http://127.0.0.1:4096/session/session-1/message", expected),
    ]
