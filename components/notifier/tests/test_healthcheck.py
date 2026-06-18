"""Unit tests for the notifier healthcheck script."""

import sys
import unittest
from datetime import UTC, datetime
from unittest.mock import Mock, patch


@patch("sys.exit")
@patch("pathlib.Path.read_text")
class NotifierHealthcheckTestCase(unittest.TestCase):
    """Unit tests for the notifier healthcheck."""

    def run_healthcheck(self) -> None:
        """Run the healthcheck."""
        import healthcheck  # noqa: F401,PLC0415

    def tearDown(self) -> None:
        """Remove the healthcheck module."""
        if "healthcheck" in sys.modules:
            del sys.modules["healthcheck"]

    def test_healthy(self, mock_read_text: Mock, mock_exit: Mock):
        """Test that the notifier is healthy if the timestamp is recent."""
        mock_read_text.return_value = datetime.now(tz=UTC).isoformat()
        self.run_healthcheck()
        mock_exit.assert_called_once_with(0)

    def test_unhealthy(self, mock_read_text: Mock, mock_exit: Mock):
        """Test that the notifier is unhealthy if the timestamp is old."""
        mock_read_text.return_value = datetime(2026, 6, 18, 0, 0, 0, tzinfo=UTC).isoformat()
        self.run_healthcheck()
        mock_exit.assert_called_once_with(1)

    def test_empty_file(self, mock_read_text: Mock, mock_exit: Mock):
        """Test that the notifier is unhealthy if the timestamp is missing."""
        mock_read_text.return_value = ""
        self.assertRaises(ValueError, self.run_healthcheck)
        mock_exit.assert_called_once_with(1)
