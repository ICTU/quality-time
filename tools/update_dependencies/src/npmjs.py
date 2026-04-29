"""npmjs."""

from functools import cache

import requests

from github import get_latest_release_json


@cache
def get_changes(package: str, version: str) -> str:
    """Return the changelog for the package and version."""
    response = requests.get(f"https://registry.npmjs.org/{package}/{version}", timeout=10)
    response.raise_for_status()
    json = response.json()
    repository_url = json["repository"]["url"]
    repository_url = repository_url.split("#")[0]
    repository_url = repository_url.removesuffix(".git")
    owner, repository = repository_url.split("/")[3:5]
    json = get_latest_release_json(owner, repository)
    return json.get("body", "")
