"""CircleCI config updater script finds images and updates to the latest versions."""

import sys
from pathlib import Path

from docker import get_latest_tag
from filesystem import update_file
from log import get_logger

LOG = get_logger("circleci")
IMAGE_RE = r"image: (?P<dependency>[\w\d\./-]+):(?P<version>[\d\w\.\-]+)"


def update_circle_ci_config(config_yml: Path) -> int:
    """Update the CircleCI config file."""
    return update_file(config_yml, IMAGE_RE, get_latest_tag, LOG)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_circle_ci_config(Path.cwd() / ".circleci" / "config.yml"))
