"""
IDE session manager.
"""

from __future__ import annotations

from uuid import uuid4

from .models import (
    IDEProject,
    IDESession,
    IDESessionStatus,
    IDEType,
)


class IDESessionManager:
    """
    Manages IDE sessions.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, IDESession] = {}

    def create(
        self,
        ide: IDEType,
        project: IDEProject | None = None,
    ) -> IDESession:
        """
        Create new IDE session.
        """

        session = IDESession(
            id=str(uuid4()),
            ide=ide,
            status=IDESessionStatus.CREATED,
            project=project,
        )

        self._sessions[session.id] = session

        return session

    def connect(
        self,
        session_id: str,
    ) -> IDESession:
        """
        Mark session as connected.
        """

        session = self._sessions[session_id]

        updated = IDESession(
            id=session.id,
            ide=session.ide,
            status=IDESessionStatus.CONNECTED,
            project=session.project,
        )

        self._sessions[session_id] = updated

        return updated

    def close(
        self,
        session_id: str,
    ) -> None:
        """
        Close IDE session.
        """

        session = self._sessions[session_id]

        self._sessions[session_id] = IDESession(
            id=session.id,
            ide=session.ide,
            status=IDESessionStatus.CLOSED,
            project=session.project,
        )

    def get(
        self,
        session_id: str,
    ) -> IDESession:
        return self._sessions[session_id]

    def list(self) -> list[IDESession]:
        return list(self._sessions.values())