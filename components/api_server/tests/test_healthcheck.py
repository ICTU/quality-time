"""Unit tests for the API-server healthcheck script."""

import unittest
from http import HTTPStatus
from unittest.mock import patch, MagicMock


class APIServerHealthcheckTestCase(unittest.TestCase):
    """Unit tests for the API-server healthcheck."""

    @patch("sys.exit")
    @patch("urllib.request.urlopen")
    def test_healthy(self, mock_urlopen, mock_exit):
        """Test that the server is healthy."""
        response = MagicMock()
        response.status = HTTPStatus.OK
        response.__enter__.return_value = response
        mock_urlopen.return_value = response
        import healthcheck  # noqa: F401

        mock_exit.assert_called_once_with(0)
