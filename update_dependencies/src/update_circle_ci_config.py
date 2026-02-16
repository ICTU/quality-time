"""CircleCI config updater script finds images and updates to the latest versions."""

import sys
from pathlib import Path

from docker import get_latest_tag
from filesystem import update_file
from log import get_logger

LOG = get_logger("circleci")
IMAGE_RE = r"image: (?P<dependency>[\w\d\./-]+):(?P<version>[\d\w\.\-]+)"


if __name__ == "__main__":  # pragma: no cover
    config_yml = Path.cwd() / ".circleci" / "config.yml"
    sys.exit(update_file(config_yml, IMAGE_RE, get_latest_tag, LOG))
