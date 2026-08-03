"""
MCP transport protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .messages import (
    MCPRequest,
    MCPResponse,
)


class MCPTransportProtocol(ABC):
    """
    Base MCP transport contract.
    """

    @abstractmethod
    def receive(self) -> MCPRequest:
        """
        Receive MCP request.
        """
        raise NotImplementedError

    @abstractmethod
    def send(
        self,
        response: MCPResponse,
    ) -> None:
        """
        Send MCP response.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Close transport.
        """
        raise NotImplementedError