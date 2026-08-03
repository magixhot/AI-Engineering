"""
IDE integration layer.
"""

from .adapters import (
    AntigravityAdapter,
    VSCodeAdapter,
)
from .models import (
    IDEProject,
    IDESession,
    IDESessionStatus,
    IDEType,
)
from .project import IDEProjectManager
from .protocol import IDEAdapterProtocol
from .session import IDESessionManager

__all__ = [
    "IDEType",
    "IDESessionStatus",
    "IDEProject",
    "IDESession",
    "IDEAdapterProtocol",
    "IDESessionManager",
    "IDEProjectManager",
    "AntigravityAdapter",
    "VSCodeAdapter",
]