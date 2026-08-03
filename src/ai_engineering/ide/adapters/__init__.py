"""
IDE adapters package.
"""

from .antigravity import AntigravityAdapter
from .vscode import VSCodeAdapter

__all__ = [
    "AntigravityAdapter",
    "VSCodeAdapter",
]