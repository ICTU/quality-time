"""Fixture for reports."""
import unittest

from .fixtures import create_report


class FixtureTest(unittest.TestCase):
    """Tests for fixtures."""

    def test_create_report(self):
        """Tests create report."""
        report1 = create_report()
        self.assertEqual(report1["report_uuid"], "report1")
        self.assertEqual(report1["title"], "Title")
        self.assertEqual(report1["subjects"]["subject_uuid"]["metrics"]["metric_uuid"]["name"], "Metric")

    def test_create_report_deleted(self):
        """Tests with deleted."""
        report_deleted = create_report(deleted=True)
        self.assertTrue(report_deleted["deleted"])
