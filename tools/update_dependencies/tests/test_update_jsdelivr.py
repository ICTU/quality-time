"""Unit tests for the jsdelivr CDN URLs update script."""

import unittest
from unittest.mock import Mock, patch

from update_jsdelivr import get_latest_version

from .helpers import mock_response


@patch("requests.get")
class UpdateJsdelivrTest(unittest.TestCase):
    """Unit tests for the get latest jsdelivr version function."""

    def test_unchanged(self, mock_get: Mock):
        """Test an unchanged version."""
        mock_get.return_value = mock_response({"tags": {"latest": "1.0"}})
        self.assertEqual("1.0", get_latest_version("clipboard", "1.0").version)

    def test_newer(self, mock_get: Mock):
        """Test an newer version."""
        mock_get.return_value = mock_response({"tags": {"latest": "1.1"}})
        self.assertEqual("1.1", get_latest_version("clipboard", "1.0").version)

    def test_older(self, mock_get: Mock):
        """Test an older version."""
        mock_get.return_value = mock_response({"tags": {"latest": "0.9"}})
        self.assertEqual("1.0", get_latest_version("clipboard", "1.0").version)

    @patch("logging.Logger.error")
    def test_invalid_version(self, mock_error: Mock, mock_get: Mock):
        """Test that the file is not written if there are no outdated packages."""
        mock_get.return_value = mock_response({})
        self.assertEqual("1.0", get_latest_version("clipboard", "1.0").version)
        mock_error.assert_called_once_with("Got an invalid version for %s: %s", "clipboard", "''", stacklevel=2)
