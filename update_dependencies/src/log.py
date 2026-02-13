"""Log helpers."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from rich.logging import RichHandler

if TYPE_CHECKING:
    from collections.abc import Callable


class UpdateLogger:
    """Wrap a logger and add update specific log methods."""

    def __init__(self, name: str) -> None:
        """Initialize the logger."""
        self.log = logging.getLogger(name)

    def new_version(self, dependency: str, new_version: str) -> None:
        """Log the availability of a new version."""
        self.log.warning("New version available for %s: %s", dependency, new_version)

    def invalid_version(self, dependency: str, invalid_version: str) -> None:
        """Log an invalid version."""
        self.log.error("Got an invalid version for %s: %s", dependency, invalid_version)

    def path(self, path: Path) -> None:
        """Log working on path."""
        self.log.info("Updating %s", path.relative_to(Path.cwd()))

    def __getattr__(self, attribute: str) -> Callable:
        """Forward calls to the wrapped logger."""
        return getattr(self.log, attribute)


def logger(name: str) -> UpdateLogger:
    """Initialize a logger."""
    logging.basicConfig(level=logging.INFO, datefmt="[%X]", format="%(message)s", handlers=[RichHandler()])
    return UpdateLogger(name)
