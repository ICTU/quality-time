"""Unit tests for the Dependency-Track licenses collector."""

import unittest

from shared_data_model import DATA_MODEL

import source_collectors  # noqa: F401
from base_collectors import SourceCollector


class DependencyTrackLicensesTest(unittest.TestCase):
    """Unit tests for the Dependency-Track licenses collector."""

    def test_licenses_metric_in_data_model(self):
        """Test that the data model has a licenses metric."""
        self.assertIn("licenses", sorted(DATA_MODEL.metrics))

    def test_licenses_collector_registered(self):
        """Test that there is a Dependency-Track collector for the licenses metric."""
        self.assertIsNotNone(SourceCollector.get_subclass("dependency_track", "licenses"))
