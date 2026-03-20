"""Log helpers."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from rich.logging import RichHandler

if TYPE_CHECKING:
    from version import DependencyVersion


class Logger:
    """Wrap a logger and add update specific log methods."""

    def __init__(self, name: str) -> None:
        """Initialize the logger."""
        self.log = logging.getLogger(name)
        self.logged_changes: set[tuple[str, DependencyVersion]] = set()

    def new_version(self, dependency: str, version: DependencyVersion) -> None:
        """Log the availability of a new version."""
        suppression_message = "Suppressing changelog already shown, see above"
        changes = suppression_message if (dependency, version) in self.logged_changes else version.changes
        self.logged_changes.add((dependency, version))
        self.log.warning("New version available for %s: %s\n%s", dependency, version.version, changes, stacklevel=2)

    def invalid_version(self, dependency: str, invalid_version: str) -> None:
        """Log an invalid version."""
        self.log.error("Got an invalid version for %s: %s", dependency, invalid_version, stacklevel=2)

    def path(self, path: Path) -> None:
        """Log working on path."""
        self.log.info("Updating %s", path.relative_to(Path.cwd()), stacklevel=2)

    def expected_node_base_image(self, dockerfile: Path) -> None:
        """Log missing Node base image."""
        self.log.error("Expected Dockerfile %s to have a Node base image", dockerfile)


def get_logger(name: str) -> Logger:
    """Initialize a logger."""
    logging.basicConfig(level=logging.INFO, datefmt="[%X]", format="%(message)s", handlers=[RichHandler()])
    return Logger(name)
