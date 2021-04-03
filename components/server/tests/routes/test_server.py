"""Unit tests for the server route."""

import unittest

from routes.server import get_server, QUALITY_TIME_VERSION


class ServerTest(unittest.TestCase):
    """Unit tests for the server route."""

    def test_server(self):
        """Test that the server info can be retrieved."""
        self.assertEqual(dict(version=QUALITY_TIME_VERSION), get_server())
