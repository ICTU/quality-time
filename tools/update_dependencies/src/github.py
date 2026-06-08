"""GitHub functions."""

import os
from dataclasses import dataclass
from datetime import datetime
from functools import cache, cached_property
from urllib.parse import urlparse

import requests
from packaging.version import Version

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

    @property
    def version(self) -> Version:
        """Return the release version."""
        return Version(self.tag_name.lstrip("v"))


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
def _list_releases(owner: str, repository: str) -> tuple[dict, ...]:
    """Fetch the GitHub releases for a repo. Returns an empty tuple when the repo can't be reached."""
    releases_url = f"https://api.github.com/repos/{owner}/{repository}/releases?per_page=100"
    try:
        response = requests.get(releases_url, headers=_github_headers(), timeout=10)
    except requests.exceptions.Timeout:
        LOG.timeout(releases_url)
        return ()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        LOG.response(response)
        return ()
    return tuple(response.json())


def get_latest_release(owner: str, repository: str) -> Release | None:
    """Get the latest eligible release from the GitHub releases API.

    Don't use the latest release endpoint, but rather get recent releases and weed out invalid versions.
    """
    candidates = (Release.from_json(owner, repository, release) for release in _list_releases(owner, repository))
    return next((r for r in candidates if r.is_eligible), None)


def get_release(owner: str, repository: str, package: str, version: str) -> Release | None:
    """Get the release matching the package and version from the GitHub releases API.

    Tries tag names in order of specificity:
    1. ``<package>-v<version>`` (monorepo, e.g. ``puppeteer-core-v25.0.4``)
    2. ``v<version>`` (e.g. ``v25.0.4``)
    3. ``<version>`` (e.g. ``25.0.4``)
    """
    releases_by_tag = {release.get("tag_name"): release for release in _list_releases(owner, repository)}
    for tag in (f"{package}-v{version}", f"v{version}", version):
        if tag in releases_by_tag:
            return Release.from_json(owner, repository, releases_by_tag[tag])
    return None


def _github_headers() -> dict[str, str]:
    """Return GitHub API request headers, including authorization if GITHUB_TOKEN is set."""
    return {"Authorization": f"Bearer {github_token}"} if (github_token := os.environ.get("GITHUB_TOKEN")) else {}
