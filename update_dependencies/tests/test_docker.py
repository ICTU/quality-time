"""Unit tests for the Docker module."""

import unittest
from unittest.mock import Mock, patch

from docker import get_latest_tag


class GetLatestTagTest(unittest.TestCase):
    """Unit tests for getting the latest tag."""

    # Note get_latest_tag uses caching, so the image name needs to be difficult for each test

    def create_mock_response(self, mock_get: Mock, json: dict) -> None:
        """Create a mock response for the mock requests.get method with the JSON result."""
        response = Mock()
        response.json.return_value = json
        mock_get.return_value = response

    def test_invalid_current_tag(self):
        """Test that the current tag is returned if it's not a valid version."""
        self.assertEqual("invalid version", get_latest_tag("image", "invalid version"))

    @patch("requests.get")
    def test_no_results(self, mock_get: Mock):
        """Test that the current tag is returned if Docker Hub has no results."""
        self.create_mock_response(mock_get, {})
        self.assertEqual("1.0", get_latest_tag("no_results", "1.0"))

    @patch("requests.get")
    def test_empty_results(self, mock_get: Mock):
        """Test that the current tag is returned if Docker Hub has an empty results list."""
        self.create_mock_response(mock_get, {"results": []})
        self.assertEqual("1.0", get_latest_tag("empty_results", "1.0"))

    @patch("requests.get")
    def test_up_to_date(self, mock_get: Mock):
        """Test that the current tag is returned if it's up to date."""
        self.create_mock_response(mock_get, {"results": [{"name": "1.0"}]})
        self.assertEqual("1.0", get_latest_tag("up_to_date", "1.0"))

    @patch("requests.get")
    def test_newer(self, mock_get: Mock):
        """Test that the current tag is returned if it's newer than the newest tag available."""
        self.create_mock_response(mock_get, {"results": [{"name": "1.0"}]})
        self.assertEqual("1.1", get_latest_tag("newer", "1.1"))

    @patch("requests.get")
    def test_new_version_available(self, mock_get: Mock):
        """Test that the new tag is returned if it's newer."""
        self.create_mock_response(mock_get, {"results": [{"name": "2.1"}]})
        self.assertEqual("2.1", get_latest_tag("new_version_available", "1.2"))

    @patch("requests.get")
    def test_multiple_new_versions_available(self, mock_get: Mock):
        """Test that the newest tag is returned if multiple newer tags are available."""
        self.create_mock_response(mock_get, {"results": [{"name": "2.2"}, {"name": "2.1"}, {"name": "2.3"}]})
        self.assertEqual("2.3", get_latest_tag("new_versions_available", "1.2"))

    @patch("requests.get")
    def test_multiple_new_versions_available_across_pages(self, mock_get: Mock):
        """Test that the newest tag is returned even if the results are paginated."""
        response1 = Mock()
        response1.json.return_value = {"results": [{"name": "2.1"}], "next": "https://example.org/next_page"}
        response2 = Mock()
        response2.json.return_value = {"results": [{"name": "2.2"}]}
        mock_get.side_effect = [response1, response2]
        self.assertEqual("2.2", get_latest_tag("pagination", "1.2"))

    @patch("requests.get")
    def test_invalid_new_tag(self, mock_get: Mock):
        """Test that invalid new tags are ignored."""
        self.create_mock_response(mock_get, {"results": [{"name": "invalid"}]})
        self.assertEqual("1.3", get_latest_tag("invalid_new_tag", "1.3"))

    @patch("requests.get")
    def test_prerelease(self, mock_get: Mock):
        """Test that prerelease tags are ignored."""
        self.create_mock_response(mock_get, {"results": [{"name": "1.4a1"}]})
        self.assertEqual("1.3", get_latest_tag("prerelease", "1.3"))

    @patch("requests.get")
    def test_different_suffix(self, mock_get: Mock):
        """Test that tags for different suffixes are ignored."""
        self.create_mock_response(mock_get, {"results": [{"name": "1.4-windows"}]})
        self.assertEqual("1.3", get_latest_tag("different_suffix", "1.3"))
