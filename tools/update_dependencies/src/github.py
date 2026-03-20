"""GitHub functions."""

import os
from functools import cache
from urllib.parse import urlparse

import requests


def github_to_raw(url: str) -> str:
    """Convert GitHub URLs to URLs that return raw content."""
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.netloc == "github.com":
        # Build the corresponding raw.githubusercontent.com URL based on the parsed path.
        raw_path = parsed.path.replace("/blob/", "/")
        return f"https://raw.githubusercontent.com{raw_path}"
    return url


def github_organization_and_repository(url: str) -> tuple[str, str]:
    """Parse the GitHub organization and repository from a URL."""
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.netloc == "github.com":
        path_parts = parsed.path.lstrip("/").split("/")
        if len(path_parts) > 1:
            return path_parts[0], path_parts[1]
    return "", ""


@cache
def get_latest_release_json(organization: str, repository: str) -> dict:
    """Get the latest release JSON from the GitHub releases API."""
    url = f"https://api.github.com/repos/{organization}/{repository}/releases/latest"
    headers = {"Authorization": f"Bearer {github_token}"} if (github_token := os.environ.get("GITHUB_TOKEN")) else {}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()
