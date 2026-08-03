"""
MCP runtime execution context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(slots=True)
class RuntimeContext:
    """
    Context of one MCP runtime execution.
    """

    session_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    metadata: dict[str, str] = field(
        default_factory=dict
    )

    def add_metadata(
        self,
        key: str,
        value: str,
    ) -> None:
        """
        Add runtime metadata.
        """

        self.metadata[key] = value