"""Docker tag updater script finds Dockerfiles and updates base image tags to latest compatible versions."""

import sys
from typing import TYPE_CHECKING

from docker import update_image_tag
from filesystem import glob
from log import logger

if TYPE_CHECKING:
    from pathlib import Path

LOG = logger("dockerfile")
IMAGE_RE = r"FROM (?P<image>[\w\d\./-]+):(?P<tag>[\d\w\.\-]+)"


def update_dockerfile(dockerfile_path: Path) -> None:
    """Update FROM statements in a Dockerfile with latest compatible tags."""
    LOG.path(dockerfile_path)
    old_lines = dockerfile_path.read_text().splitlines()
    new_lines = [update_image_tag(line, IMAGE_RE, LOG) for line in old_lines]
    if old_lines != new_lines:
        dockerfile_path.write_text("\n".join(new_lines) + "\n")


def update_dockerfiles() -> int:
    """Find all Dockerfiles under the current working directory and update them."""
    for dockerfile in glob("Dockerfile"):
        update_dockerfile(dockerfile)
    return 0


if __name__ == "__main__":
    sys.exit(update_dockerfiles())
