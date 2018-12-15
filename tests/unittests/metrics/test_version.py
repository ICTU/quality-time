"""Unit tests for the version metric."""

import unittest

from quality_time.metric import MetricStatus
from quality_time.metrics import Version


class VersionTest(unittest.TestCase):
    """Unit tests for the Version metric class."""

    def test_version_aggregation(self):
        """Test that multiple versions are comma separated."""
        self.assertRaises(ValueError, Version(dict()).sum, ["1.2", "1.1"])

    def test_status_target_met(self):
        """Test that the status is target met if the version is larger than the target version."""
        self.assertEqual(MetricStatus.target_met, Version(dict(target="1.0")).status("2.0"))

    def test_status_target_not_met(self):
        """Test that the status is target not met if the version is msaller than the target version."""
        self.assertEqual(MetricStatus.target_not_met, Version(dict(target="2.0")).status("1.0"))
