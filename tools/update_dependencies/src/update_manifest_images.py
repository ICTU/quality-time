"""Manifest image updater script finds image tags and updates them to latest compatible versions."""

import sys
from pathlib import Path

from docker import get_latest_tag
from filesystem import YAML_GLOB_PATTERNS, update_files
from log import get_logger

LOG = get_logger("manifest images")
IMAGE_RE = r"image: (?P<dependency>[\w\d\./-]+):(?P<version>[\d\w\.\-]+)@(?P<sha>sha256:[a-f0-9]{64})"


def update_manifest_images() -> int:
    """Update the image tags and digests in the Docker Compose files and the Helm folder.

    Third-party images are pinned as ``tag@sha256:digest``; both the tag and digest are kept in sync. Images
    referenced by tag only are left untouched because the regex requires a digest, so the production Helm chart
    templates (which use ``{{ ... }}`` placeholders) and Compose lines using ``${VAR}`` substitution are ignored.
    """
    results = [
        update_files("docker-compose*.yml", regexp=IMAGE_RE, get_new_version=get_latest_tag, logger=LOG),
        update_files(
            *YAML_GLOB_PATTERNS, regexp=IMAGE_RE, get_new_version=get_latest_tag, logger=LOG, start=Path.cwd() / "helm"
        ),
    ]
    return max(results)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(update_manifest_images())
