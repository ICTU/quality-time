"""Unit tests for the GitHub Action update script."""

from datetime import UTC, datetime, timedelta
from unittest.mock import ANY, Mock, patch

import requests

from update_github_action import get_latest_version

from .helpers import CacheClearingTestCase, mock_response, release_json


@patch("requests.get")
class UpdateGitHubActionTest(CacheClearingTestCase):
    """Unit tests for the get latest GitHub Action version function."""

    def test_unchanged(self, mock_get: Mock):
        """Test an unchanged version."""
        mock_get.side_effect = [
            mock_response([release_json("1.0", body="changelog")]),
            mock_response({"sha": "sha"}),
        ]
        latest_version = get_latest_version("docker/docker", "1.0")
        self.assertEqual("1.0", latest_version.version)
        self.assertEqual("changelog", latest_version.changes)

    def test_newer(self, mock_get: Mock):
        """Test an newer version."""
        mock_get.side_effect = [
            mock_response([release_json("1.1", body="changelog")]),
            mock_response({"sha": "sha"}),
        ]
        latest_version = get_latest_version("docker/hub", "1.0")
        self.assertEqual("1.1", latest_version.version)
        self.assertEqual("changelog", latest_version.changes)

    def test_publication_date(self, mock_get: Mock):
        """Test that the release's publication date is captured."""
        published = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        mock_get.side_effect = [
            mock_response([release_json("1.1", published_at=published)]),
            mock_response({"sha": "sha"}),
        ]
        self.assertEqual(datetime.fromisoformat(published), get_latest_version("docker/dated", "1.0").published)

    def test_older(self, mock_get: Mock):
        """Test an older version."""
        mock_get.side_effect = [
            mock_response([release_json("0.9")]),
            mock_response({"sha": "sha"}),
        ]
        self.assertEqual("1.0", get_latest_version("github/action", "1.0").version)

    @patch("logging.Logger.error")
    def test_no_version(self, mock_error: Mock, mock_get: Mock):
        """Test that an error is logged and the current version kept when there is no valid release."""
        mock_get.return_value = mock_response([])
        self.assertEqual("1.0", get_latest_version("docker/action", "1.0").version)
        mock_error.assert_called_once_with("No valid version found for %s", "docker/action", stacklevel=ANY)

    @patch("logging.Logger.error", Mock())
    def test_no_commit_sha(self, mock_get: Mock):
        """Test that the version is not updated when the commit SHA can't be fetched for an eligible release."""
        mock_get.side_effect = [
            mock_response([release_json("1.1")]),
            Mock(raise_for_status=Mock(side_effect=requests.exceptions.HTTPError)),
        ]
        self.assertEqual("1.0", get_latest_version("docker/no-sha-action", "1.0").version)
