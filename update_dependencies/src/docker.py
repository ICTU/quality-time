"""Get the latest available tags from Docker Hub."""

import re
from functools import cache
from typing import TYPE_CHECKING

import requests
from packaging.version import InvalidVersion, Version

if TYPE_CHECKING:
    from log import UpdateLogger


def update_image_tag(line: str, regexp: str, logger: UpdateLogger) -> str:
    """Update the tag if the Dockerfile line contains a FROM statement, otherwise return the line unchanged."""
    if match := re.match(regexp, line):
        image = match.group("image")
        tag = match.group("tag")
        latest_tag = _get_latest_tag(image, tag)
        if latest_tag != tag:
            logger.new_version(image, latest_tag)
            return line.replace(tag, latest_tag)
    return line


def _get_latest_tag(image: str, current_tag: str) -> str:
    """Find the latest compatible tag for an image. Keeps the same non-numerical parts while upgrading the version."""
    current_version, current_suffix = _split_tag(current_tag)
    if current_version is None:
        return current_tag  # Can't determine a newer tag if the tag doesn't contain a valid version
    latest_version = current_version
    for tag in _get_available_tags(image):
        version, suffix = _split_tag(tag)
        if version is None:
            continue  # Ignore tags if the version is not valid
        if version.is_prerelease:
            continue  # Ignore tags if the version is a prereleease
        if suffix != current_suffix:
            continue  # Ignore tags with a different suffix because we don't want to change e.g. fat to slim
        latest_version = max(latest_version, version)
    return _assemble_tag(latest_version, current_suffix)


@cache
def _get_available_tags(image: str) -> list[str]:
    """Fetch available tags for a Docker image from Docker Hub."""
    namespace, repository = image.split("/", maxsplit=1) if "/" in image else ("library", image)
    url = f"https://registry.hub.docker.com/v2/namespaces/{namespace}/repositories/{repository}/tags?page_size=100"
    tags = []
    while url:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        json = response.json()
        tags.extend([result["name"] for result in json.get("results", [])])
        url = json.get("next")
    return tags


def _split_tag(tag: str) -> tuple[Version | None, str]:
    """Split the tag in a version and suffix. If the tag doesn't contain a valid version, the version is None."""
    version_string, suffix = tag.split("-", maxsplit=1) if "-" in tag else (tag, "")
    try:
        version = Version(version_string)
    except InvalidVersion:
        version = None
    return version, suffix


def _assemble_tag(version: Version, suffix: str) -> str:
    """Assemble a tag from the version and suffix."""
    return f"{version}-{suffix}" if suffix else str(version)
