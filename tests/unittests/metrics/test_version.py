"""Unit tests for the version metric."""

import unittest

from quality_time.metrics import Version


class VersionTest(unittest.TestCase):
    """Unit tests for the Version metric class."""

    def test_version_aggregation(self):
        """Test that multiple versions are comma separated."""
        self.assertEqual("1.2, 1.1", Version.sum(["1.2", "1.1"]))
