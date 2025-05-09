"""Unit tests for the health route."""

import unittest

from routes import get_health


class HealthTest(unittest.TestCase):
    """Unit tests for the health route."""

    def test_health(self):
        """Test that the health status can be retrieved."""
        self.assertEqual({"healthy": True}, get_health())
