"""Unit tests for the health route."""

import unittest

from routes import get_health


class HealthTest(unittest.TestCase):
    """Unit tests for the health endpoint."""

    def test_get_health(self):
        """Test that the health status can be retrieved."""
        self.assertEqual({}, get_health())
