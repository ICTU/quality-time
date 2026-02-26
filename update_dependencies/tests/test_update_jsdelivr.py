"""Unit tests for the jsdelivr CDN URLs update script."""

import unittest
from unittest.mock import Mock, patch

from update_jsdelivr import get_latest_version


class UpdateJsdelivrTest(unittest.TestCase):
    """Unit tests for the get latest jsdelivr version function."""

    @patch("requests.get")
    def test_unchanged(self, mock_get: Mock):
        """Test an unchanged version."""
        mock_get.return_value = Mock(json=Mock(return_value={"tags": {"latest": "1.0"}}))
        self.assertEqual("1.0", get_latest_version("clipboard", "1.0"))

    @patch("requests.get")
    def test_newer(self, mock_get: Mock):
        """Test an newer version."""
        mock_get.return_value = Mock(json=Mock(return_value={"tags": {"latest": "1.1"}}))
        self.assertEqual("1.1", get_latest_version("clipboard", "1.0"))

    @patch("requests.get")
    def test_older(self, mock_get: Mock):
        """Test an older version."""
        mock_get.return_value = Mock(json=Mock(return_value={"tags": {"latest": "0.9"}}))
        self.assertEqual("1.0", get_latest_version("clipboard", "1.0"))

    @patch("logging.Logger.error")
    @patch("requests.get")
    def test_invalid_version(self, mock_get: Mock, mock_error: Mock):
        """Test that the file is not written if there are no outdated packages."""
        mock_get.return_value = Mock(json=Mock(return_value={}))
        self.assertEqual("1.0", get_latest_version("clipboard", "1.0"))
        mock_error.assert_called_once_with("Got an invalid version for %s: %s", "clipboard", "''", stacklevel=2)
