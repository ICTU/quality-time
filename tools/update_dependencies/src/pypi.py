"""Python Package Index."""

import http
import re
from functools import cache
from typing import TYPE_CHECKING

import requests

from changelog import get_version_changes_from_changelog
from github import get_latest_release_json, github_organization_and_repository, github_to_raw

if TYPE_CHECKING:
    from log import Logger


CHANGELOG_URL_KEYS = {"changes", "changelog", "release notes"}
REPOSITORY_URL_KEYS = {"repository", "source", "homepage"}


@cache
def get_changes(package: str, version: str, logger: Logger) -> str:
    """Return the changelog for the PyPI package and version.

    Since there's no standardized way that PyPI packages refer to a changelog, apply several heuristics to find it:
    - Check for changelog URLs in attributes typically used to refer to the changelog
    - Check for GitHub repository URLs in attributes in attributes typically used to refer to the source repository
      and use that to find GitHub releases
    - Check for a changelog in the package description
    - Check for a GitHub URL in the package description and use that to find GitHub releases
    """
    response = requests.get(f"https://pypi.org/pypi/{package}/{version}/json", timeout=10)
    response.raise_for_status()
    info = response.json()["info"]
    urls = info.get("project_urls", {})
    for url_key, url in urls.items():
        if url_key.lower() in CHANGELOG_URL_KEYS and (changelog := changelog_from_url(url, version, logger)):
            return changelog
    for url_key, url in urls.items():
        if url_key.lower() in REPOSITORY_URL_KEYS and (changelog := changelog_from_github_releases(url)):
            return changelog
    description = info["description"]
    return changelog_from_description(description, version) or changelog_from_github_url_in_description(description)


def changelog_from_url(url: str, version: str, logger: Logger) -> str:
    """Get the changelog from the URL."""
    changelog_response = requests.get(github_to_raw(url), timeout=10)
    if changelog_response.status_code == http.HTTPStatus.NOT_FOUND:
        logger.response(changelog_response)
        return ""
    if changelog_response.headers["Content-Type"].startswith("text/html"):
        return ""
    changelog_response.raise_for_status()
    return get_version_changes_from_changelog(changelog_response.text, version)


def changelog_from_description(description: str, version: str) -> str:
    """Get the changelog from the description."""
    return get_version_changes_from_changelog(description, version) if version in description else ""


def changelog_from_github_url_in_description(description: str) -> str:
    """Get the changelog from the description posted to PyPI."""
    github_url = r"https://github\.com/([\w.-]+)/([\w.-]+)"
    return changelog_from_github_releases(match.group()) if (match := re.search(github_url, description)) else ""


def changelog_from_github_releases(url: str) -> str:
    """Get the changelog from the GitHub releases."""
    organization, repository = github_organization_and_repository(url)
    return get_latest_release_json(organization, repository).get("body", "") if organization and repository else ""
