"""Dependency version class."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyVersion:
    """A version of a dependency."""

    version: str
    _changes: str = ""

    @property
    def changes(self) -> str:
        """Return the changelog."""
        return self._changes or "No changelog available!"
