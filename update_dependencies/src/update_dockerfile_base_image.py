"""Docker tag updater script finds Dockerfiles and updates base image tags to latest compatible versions."""

import sys

from docker import get_latest_tag
from filesystem import update_files
from log import get_logger

LOG = get_logger("dockerfile")
IMAGE_RE = r"FROM (?P<dependency>[\w\d\./-]+):(?P<version>[\d\w\.\-]+)"


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_files("Dockerfile", IMAGE_RE, get_latest_tag, LOG))
