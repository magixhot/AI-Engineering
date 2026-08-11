"""
Wire logger and Stream Wrappers for MCP Diagnostics.
Intercepts raw transport data without using the logging module.
"""

from __future__ import annotations

import datetime
from typing import Any

from .config import get_logs_dir, is_debug_enabled


class WireLogger:
    """
    Minimalist logger that writes raw wire data directly to a file.
    Does not use the `logging` module to avoid buffer/format overhead.
    """

    def __init__(self) -> None:
        if is_debug_enabled():
            self._log_file = get_logs_dir() / "mcp-wire.log"
            self._enabled = True
        else:
            self._enabled = False

    def write(self, direction: str, data: str) -> None:
        """
        Write a timestamped record to the wire log.
        direction: Usually "->" for outgoing, "<-" for incoming.
        """
        if not self._enabled:
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        record = f"{timestamp} {direction} {data.strip()}\n"

        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(record)


class LoggingReadStream:
    """
    Wraps an async text file (e.g., stdin) to log incoming traffic.
    """

    def __init__(self, stream: Any, wire_logger: WireLogger) -> None:
        self._stream = stream
        self._logger = wire_logger

    def __aiter__(self) -> LoggingReadStream:
        return self

    async def __anext__(self) -> str:
        try:
            line: str = await self._stream.__anext__()
            self._logger.write("<-", line)
            return line
        except StopAsyncIteration:
            raise


class LoggingWriteStream:
    """
    Wraps an async text file (e.g., stdout) to log outgoing traffic.
    """

    def __init__(self, stream: Any, wire_logger: WireLogger) -> None:
        self._stream = stream
        self._logger = wire_logger

    async def write(self, data: str) -> None:
        self._logger.write("->", data)
        await self._stream.write(data)

    async def flush(self) -> None:
        await self._stream.flush()


def wrap_stdio(
    stdin: Any,
    stdout: Any,
) -> tuple[Any, Any]:
    """
    Wrap stdin and stdout with Logging streams if debug is enabled.
    Returns the original streams otherwise.
    """
    if not is_debug_enabled():
        return stdin, stdout

    wire_logger = WireLogger()
    return (  # noqa: E501
        LoggingReadStream(stdin, wire_logger),
        LoggingWriteStream(stdout, wire_logger),
    )
