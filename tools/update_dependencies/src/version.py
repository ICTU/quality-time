"""Dependency version class."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from packaging.version import InvalidVersion, Version

if TYPE_CHECKING:
    from datetime import datetime


def is_valid(version: str) -> bool:
    """Return whether the version is valid."""
    try:
        Version(version)
    except InvalidVersion:
        return False
    return True


@dataclass(frozen=True)
class DependencyVersion:
    """A version of a dependency."""

    version: str  # Arbitrary version string as returned by dependency source (PyPI, Docker Hub, GitHub releases, etc.)
    _changes: str = ""
    sha: str = ""
    published: datetime | None = None

    @property
    def changes(self) -> str:
        """Return the changelog."""
        return self._changes or "No changelog available!"
