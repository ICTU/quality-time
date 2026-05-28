"""Dependency version class."""

from dataclasses import dataclass

from packaging.version import InvalidVersion, Version


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

    version: str
    _changes: str = ""
    sha: str = ""

    @property
    def changes(self) -> str:
        """Return the changelog."""
        return self._changes or "No changelog available!"
