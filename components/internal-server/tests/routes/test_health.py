"""Unit tests for the health route."""

import unittest

from routes.health import get_health


class HealthTestCase(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the health route."""

    async def test_health(self):
        """Test that the health endpoints returns the health status."""
        self.assertEqual(dict(healthy=True), await get_health())
