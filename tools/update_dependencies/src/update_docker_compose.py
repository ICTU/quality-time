"""Docker Compose file updater script finds image tags and updates them to latest compatible versions."""

import sys

from docker import get_latest_tag
from filesystem import update_files
from log import get_logger

LOG = get_logger("docker_compose")
IMAGE_RE = r"image: (?P<dependency>[\w\d\./-]+):(?P<version>[\d\w\.\-]+)"


def update_docker_compose_files() -> int:
    """Update the image tags in Docker Compose files.

    Lines using ${VAR} for the tag are left untouched because the regex does not match shell substitution syntax.
    """
    return update_files("docker-compose*.yml", IMAGE_RE, get_latest_tag, LOG)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_docker_compose_files())
