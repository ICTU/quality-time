"""Unit tests for the package.json update script."""

import unittest
from unittest.mock import Mock, patch

from update_github_action import get_latest_version


class UpdateGitHubActionTest(unittest.TestCase):
    """Unit tests for the get latest GitHub Action version function."""

    # Note get_latest_version uses caching, so the action needs to be difficult for each test

    @patch("requests.get")
    def test_unchanged(self, mock_get: Mock):
        """Test an unchanged version."""
        mock_get.return_value = Mock(json=Mock(return_value={"tag_name": "1.0"}))
        self.assertEqual("1.0", get_latest_version("docker/docker", "1.0"))

    @patch("requests.get")
    def test_newer(self, mock_get: Mock):
        """Test an newer version."""
        mock_get.return_value = Mock(json=Mock(return_value={"tag_name": "1.1"}))
        self.assertEqual("1.1", get_latest_version("docker/hub", "1.0"))

    @patch("requests.get")
    def test_older(self, mock_get: Mock):
        """Test an older version."""
        mock_get.return_value = Mock(json=Mock(return_value={"tag_name": "0.9"}))
        self.assertEqual("1.0", get_latest_version("github/action", "1.0"))

    @patch("logging.Logger.error")
    @patch("requests.get")
    def test_invalid_version(self, mock_get: Mock, mock_error: Mock):
        """Test that the package.json is not written if there are no outdated packages."""
        mock_get.return_value = Mock(json=Mock(return_value={}))
        self.assertEqual("1.0", get_latest_version("docker/action", "1.0"))
        mock_error.assert_called_once_with("Got an invalid version for %s: %s", "docker/action", "''", stacklevel=2)
