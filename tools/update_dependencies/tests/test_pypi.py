"""Unit tests for the PyPI module."""

import logging
from datetime import UTC, datetime
from http import HTTPStatus
from unittest.mock import Mock, patch

from log import get_logger
from pypi import CHANGELOG_URL_KEYS, REPOSITORY_URL_KEYS, get_changes, get_publication_datetime

from .helpers import CacheClearingTestCase, mock_response, release_json

LOG = get_logger("test_pipy")


@patch("requests.get")
class GetChangesTest(CacheClearingTestCase):
    """Unit tests for getting the changes."""

    @classmethod
    def setUpClass(cls) -> None:
        """Override to disable logging."""
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls) -> None:
        """Override to enable logging."""
        logging.disable(logging.NOTSET)

    def create_mock_response(
        self, mock_get: Mock, *json: dict | list, text: str = "", status_code: int = HTTPStatus.OK
    ) -> None:
        """Create a mock response for the mock requests.get method with the JSON result."""
        response = Mock()
        response.json.side_effect = list(json)
        response.text = text
        response.status_code = status_code
        response.headers = {"Content-Type": "text/text"}
        mock_get.return_value = response

    def test_no_url_found(self, mock_get: Mock):
        """Test that the changes are empty if no changelog URL is returned by PyPI."""
        self.create_mock_response(mock_get, {"info": {"description": "Package-foo description"}})
        self.assertEqual("", get_changes("package-1", "1.0", LOG))

    def test_changelog_url_found(self, mock_get: Mock):
        """Test that the changes are returned if a changelog URL is returned by PyPI."""
        changelog = "Changelog\n## 1.1\n- Fixed foo\n"
        for key in CHANGELOG_URL_KEYS:
            self.create_mock_response(mock_get, {"info": {"project_urls": {key: "https://changes"}}}, text=changelog)
            self.assertEqual("## 1.1\n- Fixed foo", get_changes(f"package-2-{key}", "1.1", LOG))

    def test_changelog_url_gives_404(self, mock_get: Mock):
        """Test that changelog URLs are skipped if they result in a 404."""
        for key in CHANGELOG_URL_KEYS:
            self.create_mock_response(
                mock_get,
                {"info": {"description": "Package-foo description", "project_urls": {key: "https://changes"}}},
                status_code=HTTPStatus.NOT_FOUND,
            )
            self.assertEqual("", get_changes(f"package-3-{key}", "1.1", LOG))

    def test_repository_url_found(self, mock_get: Mock):
        """Test that the changes are returned if a repository URL is returned by PyPI."""
        changelog = "Changelog\n## 1.1\n- Fixed foo\n"
        repo = "https://github.com/org/repo"
        docs = "https://docs"
        for key in REPOSITORY_URL_KEYS:
            self.create_mock_response(
                mock_get,
                {"info": {"project_urls": {"docs": docs, key: repo}}},
                [release_json("1.1", body=changelog)],
                {"sha": "sha"},
            )
            self.assertEqual(changelog, get_changes(f"package-4-{key}", "1.1", LOG))

    def test_changelog_in_description(self, mock_get: Mock):
        """Test that the changelog from the description is returned."""
        changelog = "1.1\n- Fixed ...\n- Added ..."
        self.create_mock_response(mock_get, {"info": {"description": f"Package description\n{changelog}\n"}})
        self.assertEqual(changelog, get_changes("package-5", "1.1", LOG))

    def test_github_url_in_description_that_has_a_changelog(self, mock_get: Mock):
        """Test that the GitHub URL in the description is used to get the changelog."""
        github_url = "https://github.com/org/bar"
        changelog = "1.1\n- Fixed ...\n- Added ..."
        self.create_mock_response(
            mock_get,
            {"info": {"description": f"Package description\n{github_url}\n"}},
            [release_json("1.1", body=changelog)],
            {"sha": "sha"},
        )
        self.assertEqual(changelog, get_changes("package-6", "1.1", LOG))

    def test_github_url_in_description_that_has_no_changelog(self, mock_get: Mock):
        """Test that the GitHub URL in the description is used to get the changelog."""
        github_url = "https://github.com/org/baz"
        self.create_mock_response(
            mock_get,
            {"info": {"description": f"Package description\n{github_url}\n"}},
            [release_json("1.1")],
            {"sha": "sha"},
        )
        self.assertEqual("", get_changes("package-7", "1.1", LOG))


class GetPublicationDateTimeTest(CacheClearingTestCase):
    """Unit tests for getting the publication date time of releases."""

    @patch("requests.get")
    def test_publication_datetime(self, mock_get: Mock):
        """Test that the publication datetime is returned."""
        mock_get.return_value = mock_response({"urls": [{"upload_time_iso_8601": "2026-05-30T12:00:03.678901Z"}]})
        published = datetime(2026, 5, 30, 12, 0, 3, 678901, tzinfo=UTC)
        self.assertEqual(published, get_publication_datetime("package", "1.0"))

    @patch("requests.get")
    def test_max_publication_datetime(self, mock_get: Mock):
        """Test that the latest publication datetime is returned if there are multiple distributions."""
        mock_get.return_value = mock_response(
            {
                "urls": [
                    {"upload_time_iso_8601": "2026-05-30T12:00:03.678901Z"},
                    {"upload_time_iso_8601": "2026-05-30T12:00:03.543210Z"},
                ]
            }
        )
        published = datetime(2026, 5, 30, 12, 0, 3, 678901, tzinfo=UTC)
        self.assertEqual(published, get_publication_datetime("package", "1.0"))
