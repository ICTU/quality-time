"""Unit tests for the API-server healthcheck script."""

import sys
import unittest
from http import HTTPStatus
from unittest.mock import patch, MagicMock


@patch("sys.exit")
@patch("urllib.request.urlopen")
class APIServerHealthcheckTestCase(unittest.TestCase):
    """Unit tests for the API-server healthcheck."""

    def create_response(self, healthy: bool = True, status=HTTPStatus.OK) -> MagicMock:
        """Create a API-server response."""
        response = MagicMock()
        response.status = status
        response.read.return_value = b'{"healthy": true}' if healthy else b'{"healthy": false}'
        response.__enter__.return_value = response
        return response

    def run_healthcheck(self) -> None:
        """Run the healthcheck."""
        import healthcheck  # noqa: F401,PLC0415

    def tearDown(self) -> None:
        """Remove the healthcheck module."""
        del sys.modules["healthcheck"]

    def test_healthy(self, mock_urlopen, mock_exit):
        """Test that the server is healthy."""
        mock_urlopen.return_value = self.create_response()
        self.run_healthcheck()
        mock_exit.assert_called_once_with(0)

    def test_unhealthy_json(self, mock_urlopen, mock_exit):
        """Test that the server is unhealthy."""
        mock_urlopen.return_value = self.create_response(healthy=False)
        self.run_healthcheck()
        mock_exit.assert_called_once_with(1)

    def test_unhealthy_status(self, mock_urlopen, mock_exit):
        """Test that the server is unhealthy."""
        mock_urlopen.return_value = self.create_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        self.run_healthcheck()
        mock_exit.assert_called_once_with(1)
