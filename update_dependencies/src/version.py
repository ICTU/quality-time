"""Dependency version class."""

from dataclasses import dataclass


@dataclass
class DependencyVersion:
    """A version of a dependency."""

    version: str
    changes: str = ""

    def __post_init__(self) -> None:
        """Fix an empty change log."""
        if not self.changes:
            self.changes = "No changelog available!"
