"""
IDE project management.
"""

from __future__ import annotations

from pathlib import Path

from .models import IDEProject


class IDEProjectManager:
    """
    Manages projects opened through IDE adapters.
    """

    def open(
        self,
        path: str,
    ) -> IDEProject:
        """
        Open project from filesystem path.
        """

        project_path = Path(path)

        if not project_path.exists():
            raise FileNotFoundError(
                f"Project path does not exist: {path}"
            )

        return IDEProject(
            name=project_path.name,
            path=str(project_path.resolve()),
        )

    def validate(
        self,
        project: IDEProject,
    ) -> bool:
        """
        Validate project location.
        """

        return Path(project.path).exists()