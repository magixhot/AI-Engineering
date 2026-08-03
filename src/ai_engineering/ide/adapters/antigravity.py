"""
Antigravity IDE adapter.

Initial implementation of the IDE integration layer.
"""

from __future__ import annotations

from ..models import (
    IDEProject,
    IDESession,
    IDESessionStatus,
    IDEType,
)
from ..protocol import IDEAdapterProtocol


class AntigravityAdapter(IDEAdapterProtocol):
    """
    Adapter for Antigravity IDE.

    This is a minimal working adapter.
    Transport communication will be added later.
    """

    @property
    def ide_type(self) -> IDEType:
        return IDEType.ANTIGRAVITY

    def connect(
        self,
        project: IDEProject,
    ) -> IDESession:
        """
        Create Antigravity IDE session.
        """

        return IDESession(
            id="antigravity-session",
            ide=IDEType.ANTIGRAVITY,
            status=IDESessionStatus.CONNECTED,
            project=project,
        )

    def disconnect(
        self,
        session: IDESession,
    ) -> None:
        """
        Close Antigravity session.

        Placeholder for future MCP transport.
        """

        return None

    def send_command(
        self,
        session: IDESession,
        command: str,
        payload: dict | None = None,
    ) -> dict:
        """
        Send command to Antigravity.

        Real transport will be implemented
        through MCP communication layer.
        """

        return {
            "ide": self.ide_type.value,
            "session": session.id,
            "command": command,
            "payload": payload or {},
            "status": "accepted",
        }