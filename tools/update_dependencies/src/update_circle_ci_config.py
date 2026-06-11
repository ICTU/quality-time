"""CircleCI config updater script finds images and updates to the latest versions."""

import sys
from pathlib import Path

from docker import get_latest_tag
from filesystem import YAML_GLOB_PATTERNS, update_files
from log import get_logger

LOG = get_logger("circleci")
IMAGE_RE = r"image: (?P<dependency>[\w\d\./-]+):(?P<version>[\d\w\.\-]+)@(?P<sha>sha256:[a-f0-9]{64})"


def update_circle_ci_config(circle_ci_dir: Path) -> int:
    """Update the images in all YAML files under the CircleCI directory."""
    return update_files(
        *YAML_GLOB_PATTERNS, regexp=IMAGE_RE, get_new_version=get_latest_tag, logger=LOG, start=circle_ci_dir
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_circle_ci_config(Path.cwd() / ".circleci"))
