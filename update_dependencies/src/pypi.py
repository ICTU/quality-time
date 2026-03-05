"""Python Package Index."""

from functools import cache

import requests

from changelog import get_version_changes_from_changelog
from github import get_latest_release_json, github_organization_and_repository, github_to_raw

CHANGELOG_URL_KEYS = {"changes", "changelog", "release notes"}
REPOSITORY_URL_KEYS = {"repository"}


@cache
def get_changes(package: str, version: str) -> str:
    """Return the changelog for the package and version."""
    response = requests.get(f"https://pypi.org/pypi/{package}/{version}/json", timeout=10)
    response.raise_for_status()
    json = response.json()
    urls = json["info"].get("project_urls", {})
    for url_key, url in urls.items():
        if url_key.lower() in CHANGELOG_URL_KEYS:
            changelog_response = requests.get(github_to_raw(url), timeout=10)
            changelog_response.raise_for_status()
            return get_version_changes_from_changelog(changelog_response.text, version)
    for url_key, url in urls.items():
        if url_key.lower() in REPOSITORY_URL_KEYS:
            organization, repository = github_organization_and_repository(url)
            if organization and repository:
                json = get_latest_release_json(organization, repository)
                return json.get("body", "")
    return ""
