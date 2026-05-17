"""GitHub functions."""

import os
from dataclasses import dataclass
from datetime import datetime
from functools import cache, cached_property
from urllib.parse import urlparse

import requests

from cooldown import within_cooldown
from log import get_logger
from version import is_valid

LOG = get_logger("github")


@dataclass(frozen=True)
class Release:
    """A release from the GitHub releases endpoint."""

    owner: str
    repository: str
    tag_name: str
    body: str = ""
    draft: bool = False
    prerelease: bool = False
    published_at: datetime | None = None

    @classmethod
    def from_json(cls, owner: str, repository: str, release: dict) -> Release:
        """Create a Release from a GitHub releases endpoint result."""
        published_at = release.get("published_at")
        return cls(
            owner=owner,
            repository=repository,
            tag_name=release.get("tag_name", ""),
            body=release.get("body", ""),
            draft=release.get("draft", False),
            prerelease=release.get("prerelease", False),
            published_at=datetime.fromisoformat(published_at) if published_at else None,
        )

    @property
    def has_valid_version(self) -> bool:
        """Return whether the release tag is a valid version."""
        return is_valid(self.tag_name)

    @property
    def within_cooldown(self) -> bool:
        """Return whether the release was published within the configured cooldown period."""
        return within_cooldown(self.published_at)

    @property
    def is_eligible(self) -> bool:
        """Return whether this release is eligible to be used as the latest release."""
        return not self.draft and not self.prerelease and self.has_valid_version and not self.within_cooldown

    @cached_property
    def commit_sha(self) -> str | None:
        """Fetch the commit SHA for this release's tag, or None if the commits endpoint can't be reached."""
        dependency = f"{self.owner}/{self.repository}"
        commits_url = f"https://api.github.com/repos/{dependency}/commits/{self.tag_name}"
        response = requests.get(commits_url, headers=_github_headers(), timeout=10)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            LOG.no_commit_sha(
                dependency, self.tag_name, f"https://github.com/{dependency}/releases/tag/{self.tag_name}"
            )
            return None
        return response.json()["sha"]


def github_to_raw(url: str) -> str:
    """Convert GitHub URLs to URLs that return raw content."""
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.netloc == "github.com":
        # Build the corresponding raw.githubusercontent.com URL based on the parsed path.
        raw_path = parsed.path.replace("/blob/", "/")
        return f"https://raw.githubusercontent.com{raw_path}"
    return url


def github_owner_and_repository(url: str) -> tuple[str, str]:
    """Parse the GitHub owner and repository from a URL."""
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.netloc == "github.com":
        path_parts = parsed.path.lstrip("/").split("/")
        if len(path_parts) > 1:
            return path_parts[0], path_parts[1]
    return "", ""


@cache
def get_latest_release(owner: str, repository: str) -> Release | None:
    """Get the latest eligible release from the GitHub releases API.

    Don't use the latest release endpoint, but rather get recent releases and weed out invalid versions.
    """
    releases_url = f"https://api.github.com/repos/{owner}/{repository}/releases"
    response = requests.get(releases_url, headers=_github_headers(), timeout=10)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return None
    releases = (Release.from_json(owner, repository, release) for release in response.json())
    return next((r for r in releases if r.is_eligible), None)


def _github_headers() -> dict[str, str]:
    """Return GitHub API request headers, including authorization if GITHUB_TOKEN is set."""
    return {"Authorization": f"Bearer {github_token}"} if (github_token := os.environ.get("GITHUB_TOKEN")) else {}
