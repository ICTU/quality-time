"""Get the latest available tags from Docker Hub."""

import os
from dataclasses import dataclass
from datetime import datetime
from functools import cache
from typing import cast

import requests
from packaging.version import InvalidVersion, Version

from cooldown import within_cooldown
from version import DependencyVersion


@dataclass(frozen=True)
class Tag:
    """A result from the Docker Hub tags endpoint."""

    name: str
    digest: str = ""
    last_pushed: datetime | None = None

    @classmethod
    def from_json(cls, tag: dict) -> Tag:
        """Create a Tag from a Docker Hub tags endpoint result."""
        last_pushed = tag.get("tag_last_pushed")
        last_pushed_datetime_or_none = datetime.fromisoformat(last_pushed) if last_pushed else None
        return cls(name=tag["name"], digest=tag.get("digest", ""), last_pushed=last_pushed_datetime_or_none)

    @property
    def version(self) -> Version | None:
        """Return the parsed version, or None if the tag does not contain a valid version."""
        version_string = self.name.split("-", maxsplit=1)[0]
        try:
            return Version(version_string)
        except InvalidVersion:
            return None

    @property
    def suffix(self) -> str:
        """Return the non-version suffix of the tag (e.g., 'slim' in '3.12-slim'), or empty string if none."""
        return self.name.split("-", maxsplit=1)[1] if "-" in self.name else ""

    @property
    def within_cooldown(self) -> bool:
        """Return whether the tag was pushed within the configured cooldown period."""
        return within_cooldown(self.last_pushed)

    def with_version(self, version: Version) -> Tag:
        """Return a new Tag with the same suffix but the given version."""
        name = f"{version}-{self.suffix}" if self.suffix else str(version)
        return Tag(name=name)

    def is_eligible_as_update_of(self, current: Tag) -> bool:
        """Return whether this tag is eligible as an update of the current tag."""
        if self.version is None:
            return False  # Ignore tags if the version is not valid
        if not self.digest:
            return False  # Ignore tags without digest
        if self.version.is_prerelease:
            return False  # Ignore tags if the version is a prerelease
        if self.suffix != current.suffix:
            return False  # Ignore tags with a different suffix because we don't want to change e.g. fat to slim
        return not self.within_cooldown  # Ignore tags pushed within the cooldown period


def get_latest_tag(image: str, current_tag: str) -> DependencyVersion:
    """Find the latest compatible tag for an image. Keeps the same non-numerical parts while upgrading the version."""
    current = Tag(name=current_tag)
    if current.version is None:
        # Can't determine a newer tag if the tag doesn't contain a valid version
        return DependencyVersion(version=current_tag)
    latest_version = current.version
    sha = ""
    for tag in _get_available_tags(image):
        if tag.is_eligible_as_update_of(current):
            tag_version = cast("Version", tag.version)
            if tag_version > latest_version:
                latest_version = tag_version
                sha = tag.digest
    return DependencyVersion(version=current.with_version(latest_version).name, sha=sha)


@cache
def _get_available_tags(image: str) -> list[Tag]:
    """Fetch available tags for a Docker image from Docker Hub."""
    namespace, repository = image.split("/", maxsplit=1) if "/" in image else ("library", image)
    url = f"https://registry.hub.docker.com/v2/namespaces/{namespace}/repositories/{repository}/tags?page_size=100"
    tags: list[Tag] = []
    while url:
        response = requests.get(url, headers=_docker_hub_headers(), timeout=10)
        response.raise_for_status()
        json = response.json()
        tags.extend(Tag.from_json(result) for result in json.get("results", []))
        url = json.get("next")
    return tags


@cache
def _docker_hub_headers() -> dict[str, str]:
    """Return Docker Hub API request headers with bearer token if DOCKER_HUB_USERNAME and DOCKER_HUB_TOKEN are set."""
    if (token := os.environ.get("DOCKER_HUB_TOKEN")) and (username := os.environ.get("DOCKER_HUB_USERNAME")):
        url = "https://hub.docker.com/v2/auth/token"
        response = requests.post(url, timeout=10, json={"identifier": username, "secret": token})
        response.raise_for_status()
        return {"Authorization": f"Bearer {response.json()['access_token']}"}
    return {}
