"""Unit tests for the database initialization."""

import unittest

from initialization.database import quality_time_database


class DatabaseTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the database initialization."""

    async def test_database_is_cached(self):
        """Test that foo."""
        database = await quality_time_database()
        self.assertIs(database, await quality_time_database())
