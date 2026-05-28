"""Unit tests for the package.json update script."""

import unittest
from unittest.mock import Mock, patch

import requests

from update_github_action import get_latest_version

from .helpers import mock_response


@patch("requests.get")
class UpdateGitHubActionTest(unittest.TestCase):
    """Unit tests for the get latest GitHub Action version function."""

    # Note get_latest_version uses caching, so the action needs to be difficult for each test

    def test_unchanged(self, mock_get: Mock):
        """Test an unchanged version."""
        mock_get.side_effect = [
            mock_response([{"draft": False, "prerelease": False, "tag_name": "1.0", "body": "changelog"}]),
            mock_response({"sha": "sha"}),
        ]
        latest_version = get_latest_version("docker/docker", "1.0")
        self.assertEqual("1.0", latest_version.version)
        self.assertEqual("changelog", latest_version.changes)

    def test_newer(self, mock_get: Mock):
        """Test an newer version."""
        mock_get.side_effect = [
            mock_response([{"draft": False, "prerelease": False, "tag_name": "1.1", "body": "changelog"}]),
            mock_response({"sha": "sha"}),
        ]
        latest_version = get_latest_version("docker/hub", "1.0")
        self.assertEqual("1.1", latest_version.version)
        self.assertEqual("changelog", latest_version.changes)

    def test_older(self, mock_get: Mock):
        """Test an older version."""
        mock_get.side_effect = [
            mock_response([{"draft": False, "prerelease": False, "tag_name": "0.9"}]),
            mock_response({"sha": "sha"}),
        ]
        self.assertEqual("1.0", get_latest_version("github/action", "1.0").version)

    @patch("logging.Logger.error")
    def test_no_version(self, mock_error: Mock, mock_get: Mock):
        """Test that the package.json is not written if there are no outdated packages."""
        mock_get.return_value = mock_response([])
        self.assertEqual("1.0", get_latest_version("docker/action", "1.0").version)
        mock_error.assert_called_once_with("No valid version found for %s", "docker/action", stacklevel=2)

    @patch("logging.Logger.error", Mock())
    def test_no_commit_sha(self, mock_get: Mock):
        """Test that the version is not updated when the commit SHA can't be fetched for an eligible release."""
        mock_get.side_effect = [
            mock_response([{"draft": False, "prerelease": False, "tag_name": "1.1"}]),
            Mock(raise_for_status=Mock(side_effect=requests.exceptions.HTTPError)),
        ]
        self.assertEqual("1.0", get_latest_version("docker/no-sha-action", "1.0").version)
