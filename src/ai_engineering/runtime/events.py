"""
MCP runtime events.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class RuntimeEventType(str, Enum):
    """
    Runtime event types.
    """

    STARTED = "started"
    TOOL_CALLED = "tool_called"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"
    STOPPED = "stopped"


@dataclass(slots=True, frozen=True)
class RuntimeEvent:
    """
    Runtime event record.
    """

    type: RuntimeEventType
    message: str
    timestamp: datetime


def create_event(
    event_type: RuntimeEventType,
    message: str,
) -> RuntimeEvent:
    """
    Create runtime event.
    """

    return RuntimeEvent(
        type=event_type,
        message=message,
        timestamp=datetime.now(
            timezone.utc
        ),
    )