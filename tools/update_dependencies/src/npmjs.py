"""npmjs."""

from datetime import datetime
from functools import cache

import requests

from github import get_release


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
    release = get_release(owner, repository, package, version)
    return release.body if release else ""


@cache
def get_publication_datetime(package: str, version: str) -> datetime:
    """Return the datetime that the version of the package was published."""
    response = requests.get(f"https://registry.npmjs.org/{package}", timeout=10)
    response.raise_for_status()
    json = response.json()
    return datetime.fromisoformat(json["time"][version])
