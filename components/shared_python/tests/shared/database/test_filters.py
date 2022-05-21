"""Test the database filters."""

import unittest

from shared.database import filters


class TestFilters(unittest.TestCase):
    """Test the database filters."""

    def test_filters(self):
        """Test the filters."""
        self.assertTrue(filters.DOES_EXIST["$exists"])
        self.assertFalse(filters.DOES_NOT_EXIST["$exists"])
