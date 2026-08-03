"""
IDE protocol definition.

Defines the common contract for all IDE adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import (
    IDEProject,
    IDESession,
    IDEType,
)


class IDEAdapterProtocol(ABC):
    """
    Base protocol for IDE integrations.
    """

    @property
    @abstractmethod
    def ide_type(self) -> IDEType:
        """
        Return adapter IDE type.
        """
        raise NotImplementedError

    @abstractmethod
    def connect(
        self,
        project: IDEProject,
    ) -> IDESession:
        """
        Create IDE session.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(
        self,
        session: IDESession,
    ) -> None:
        """
        Close IDE session.
        """
        raise NotImplementedError

    @abstractmethod
    def send_command(
        self,
        session: IDESession,
        command: str,
        payload: dict | None = None,
    ) -> dict:
        """
        Send command to IDE.
        """
        raise NotImplementedError