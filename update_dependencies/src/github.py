"""GitHub functions."""

import os
from functools import cache

import requests


def github_to_raw(url: str) -> str:
    """Convert GitHub URLs to URLs that return raw content."""
    if url.startswith("https://github.com"):
        return url.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob/", "/")
    return url


@cache
def get_latest_release_json(organization: str, repository: str) -> dict:
    """Get the latest release JSON from the GitHub releases API."""
    url = f"https://api.github.com/repos/{organization}/{repository}/releases/latest"
    headers = {"Authorization": f"Bearer {github_token}"} if (github_token := os.environ.get("GITHUB_TOKEN")) else {}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()
