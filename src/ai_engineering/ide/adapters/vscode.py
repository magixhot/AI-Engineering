"""
VS Code IDE adapter.

Reference implementation for future IDE integrations.
"""

from __future__ import annotations

from ..models import (
    IDEProject,
    IDESession,
    IDESessionStatus,
    IDEType,
)
from ..protocol import IDEAdapterProtocol


class VSCodeAdapter(IDEAdapterProtocol):
    """
    Adapter for Visual Studio Code.

    Minimal implementation.
    """

    @property
    def ide_type(self) -> IDEType:
        return IDEType.VSCODE

    def connect(
        self,
        project: IDEProject,
    ) -> IDESession:
        """
        Create VS Code session.
        """

        return IDESession(
            id="vscode-session",
            ide=IDEType.VSCODE,
            status=IDESessionStatus.CONNECTED,
            project=project,
        )

    def disconnect(
        self,
        session: IDESession,
    ) -> None:
        """
        Close VS Code session.
        """

        return None

    def send_command(
        self,
        session: IDESession,
        command: str,
        payload: dict | None = None,
    ) -> dict:
        """
        Send command to VS Code.

        Transport layer will be implemented later.
        """

        return {
            "ide": self.ide_type.value,
            "session": session.id,
            "command": command,
            "payload": payload or {},
            "status": "accepted",
        }