"""CircleCI config updater script finds images and updates to the latest versions."""

import sys
from pathlib import Path

from docker import update_image_tag
from log import logger

LOG = logger("circleci")
IMAGE_RE = r"image: (?P<image>[\w\d\./-]+):(?P<tag>[\d\w\.\-]+)"


def update_circle_ci_config() -> int:
    """Update images in the Circle CI config."""
    config_yml = Path.cwd() / ".circleci" / "config.yml"
    LOG.path(config_yml)
    old_lines = config_yml.read_text().splitlines()
    new_lines = [update_image_tag(line, IMAGE_RE, LOG) for line in old_lines]
    if old_lines != new_lines:
        config_yml.write_text("\n".join(new_lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(update_circle_ci_config())
