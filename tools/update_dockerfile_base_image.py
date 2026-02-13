# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "packaging>=26.0",
#     "requests>=2.32.5",
# ]
# ///

"""Docker tag updater script finds Dockerfiles and updates base image tags to latest compatible versions."""

import re
import sys
from functools import cache
from pathlib import Path

import requests
from packaging.version import InvalidVersion, Version


@cache
def get_available_tags(image: str) -> list[str]:
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


def split_tag(tag: str) -> tuple[Version | None, str]:
    """Split the tag in a version and suffix. If the tag doesn't contain a valid version, the version is None."""
    version_string, suffix = tag.split("-", maxsplit=1) if "-" in tag else (tag, "")
    try:
        version = Version(version_string)
    except InvalidVersion:
        version = None
    return version, suffix


def assemble_tag(version: Version, suffix: str) -> str:
    """Assemble a tag from the version and suffix."""
    return f"{version}-{suffix}" if suffix else str(version)


def get_latest_tag(image: str, current_tag: str) -> str:
    """Find the latest compatible tag for an image. Keeps the same non-numerical parts while upgrading the version."""
    current_version, current_suffix = split_tag(current_tag)
    if current_version is None:
        return current_tag  # Can't determine a newer tag if the tag doesn't contain a valid version
    latest_version = current_version
    for tag in get_available_tags(image):
        version, suffix = split_tag(tag)
        if version is None:
            continue  # Ignore tags if the version is not valid
        if version.is_prerelease:
            continue  # Ignore tags if the version is a prereleease
        if suffix != current_suffix:
            continue  # Ignore tags with a different suffix because we don't want to change e.g. fat to slim
        latest_version = max(latest_version, version)
    return assemble_tag(latest_version, current_suffix)


def update_dockerfile_line(line: str) -> str:
    """Update the tag if the Dockerfile line contains a FROM statement, otherwise return the line unchanged."""
    if match := re.match(r"FROM (?P<image>[\w\d\./-]+):(?P<tag>[\d\w\.\-]+)", line):
        image = match.group("image")
        tag = match.group("tag")
        return line.replace(tag, get_latest_tag(image, tag))
    return line


def update_dockerfile(dockerfile_path: Path) -> None:
    """Update FROM statements in a Dockerfile with latest compatible tags."""
    old_lines = dockerfile_path.read_text().splitlines()
    new_lines = [update_dockerfile_line(line) for line in old_lines]
    if old_lines != new_lines:
        dockerfile_path.write_text("\n".join(new_lines) + "\n")


def update_dockerfiles() -> int:
    """Find all Dockerfiles under the current working directory and update them."""
    for dockerfile in Path.cwd().rglob("Dockerfile"):
        update_dockerfile(dockerfile)
    return 0


if __name__ == "__main__":
    sys.exit(update_dockerfiles())
