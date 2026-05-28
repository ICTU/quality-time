"""Shared test helpers."""

import unittest
from unittest.mock import Mock

from docker import _docker_hub_headers, _get_available_tags
from github import _list_releases
from npmjs import get_changes as npmjs_get_changes
from pypi import get_changes as pypi_get_changes
from update_github_action import get_latest_version


class CacheClearingTestCase(unittest.TestCase):
    """Base test case that clears all functools caches before each test to prevent cross-test leakage.

    This is the single place where the cached functions need to be listed. Add new @cache'd functions here.
    """

    CACHES = (
        _docker_hub_headers,
        _get_available_tags,
        _list_releases,
        npmjs_get_changes,
        pypi_get_changes,
        get_latest_version,
    )

    def setUp(self) -> None:
        """Clear all caches so each test gets fresh results."""
        super().setUp()
        for cache in self.CACHES:
            cache.cache_clear()


def mock_response(json: dict | list | None = None, **kwargs: object) -> Mock:
    """Return a mock requests Response whose .json() returns the given value.

    Extra response attributes (text, status_code, headers, ...) can be set via keyword arguments.
    """
    response = Mock(json=Mock(return_value=json))
    response.configure_mock(**kwargs)
    return response


def mock_path(content: str) -> Mock:
    """Return a mock Path with the given text content and a no-op relative_to()."""
    return Mock(relative_to=Mock(return_value=Mock(parts=[])), read_text=Mock(return_value=content))
