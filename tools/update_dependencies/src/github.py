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


def github_owner_and_repository(url: str) -> tuple[str, str]:
    """Parse the GitHub owner and repository from a URL."""
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.netloc == "github.com":
        path_parts = parsed.path.lstrip("/").split("/")
        if len(path_parts) > 1:
            return path_parts[0], path_parts[1]
    return "", ""


@cache
def get_latest_release_json(owner: str, repository: str) -> dict:
    """Get the latest release JSON from the GitHub releases API. Also add the sha of the commit."""
    headers = {"Authorization": f"Bearer {github_token}"} if (github_token := os.environ.get("GITHUB_TOKEN")) else {}
    releases_url = f"https://api.github.com/repos/{owner}/{repository}/releases/latest"
    releases_response = requests.get(releases_url, headers=headers, timeout=10)
    try:
        releases_response.raise_for_status()
    except requests.exceptions.HTTPError:
        return {}
    json = releases_response.json()
    if "tag_name" not in json:
        return {}
    commits_url = f"https://api.github.com/repos/{owner}/{repository}/commits/{json['tag_name']}"
    commits_response = requests.get(commits_url, headers=headers, timeout=10)
    try:
        commits_response.raise_for_status()
    except requests.exceptions.HTTPError:
        return {}
    json["commit_sha"] = commits_response.json()["sha"]
    return json
