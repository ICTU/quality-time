"""Log helpers."""

import logging
from pathlib import Path

from rich.logging import RichHandler


class UpdateLogger:
    """Wrap a logger and add update specific log methods."""

    def __init__(self, name: str) -> None:
        """Initialize the logger."""
        self.log = logging.getLogger(name)

    def new_version(self, dependency: str, new_version: str) -> None:
        """Log the availability of a new version."""
        self.log.warning("New version available for %s: %s", dependency, new_version, stacklevel=2)

    def invalid_version(self, dependency: str, invalid_version: str) -> None:
        """Log an invalid version."""
        self.log.error("Got an invalid version for %s: %s", dependency, invalid_version, stacklevel=2)

    def path(self, path: Path) -> None:
        """Log working on path."""
        self.log.info("Updating %s", path.relative_to(Path.cwd()), stacklevel=2)


def logger(name: str) -> UpdateLogger:
    """Initialize a logger."""
    logging.basicConfig(level=logging.INFO, datefmt="[%X]", format="%(message)s", handlers=[RichHandler()])
    return UpdateLogger(name)
