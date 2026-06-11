"""Shared test helpers."""

import unittest
from typing import TYPE_CHECKING
from unittest.mock import ANY, Mock

from docker import _docker_hub_headers as docker_hub_headers
from docker import _get_available_tags as docker_hub_get_available_tags
from github import _list_releases as github_list_release
from npmjs import get_changes as npmjs_get_changes
from npmjs import get_publication_datetime as npmjs_get_publication_datetime
from pypi import release_metadata as pypi_release_metadata
from update_github_action import get_latest_version as github_get_latest_version
from version import DependencyVersion

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping


class CacheClearingTestCase(unittest.TestCase):
    """Base test case that clears all functools caches before each test to prevent cross-test leakage.

    This is the single place where the cached functions need to be listed. Add new @cache'd functions here.
    """

    CACHES = (
        docker_hub_get_available_tags,
        docker_hub_headers,
        github_get_latest_version,
        github_list_release,
        npmjs_get_changes,
        npmjs_get_publication_datetime,
        pypi_release_metadata,
    )

    def setUp(self) -> None:
        """Clear all caches so each test gets fresh results."""
        super().setUp()
        for cache in self.CACHES:
            cache.cache_clear()


def new_version_getter(version: str, sha: str = "") -> Callable[[str, str], DependencyVersion]:
    """Return a new-version-getter."""
    return lambda *_args: DependencyVersion(version=version, sha=sha)


def mock_response(json: Mapping | list | None = None, **kwargs: object) -> Mock:
    """Return a mock requests Response whose .json() returns the given value.

    Extra response attributes (text, status_code, headers, ...) can be set via keyword arguments.
    """
    response = Mock(json=Mock(return_value=json))
    response.configure_mock(**kwargs)
    return response


def mock_path(content: str) -> Mock:
    """Return a mock Path with the given text content and a no-op relative_to()."""
    return Mock(relative_to=Mock(return_value=Mock(parts=[])), read_text=Mock(return_value=content))


def release_json(tag_name: str, **extra: object) -> dict[str, object]:
    """Return a GitHub release API result for the tag, eligible (not a draft or prerelease) unless overridden."""
    return {"draft": False, "prerelease": False, "tag_name": tag_name, **extra}


def assert_new_version_logged(
    mock_warning: Mock, dependency: str, version: str, changes: str = "No changelog available!", *, once: bool = False
) -> None:
    """Assert that the availability of a new version was logged as a warning for the dependency."""
    assert_called = mock_warning.assert_called_once_with if once else mock_warning.assert_called_with
    assert_called("New version available for %s: %s\n%s", dependency, version, changes, stacklevel=ANY)


def assert_path_logged(mock_info: Mock, relative_path: object) -> None:
    """Assert that the file being updated was logged as info."""
    mock_info.assert_called_with("Updating %s", relative_path, stacklevel=ANY)
