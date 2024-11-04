"""Unit tests for the report data fixture."""

import unittest

from .fixtures import METRIC_ID, REPORT_ID, SUBJECT_ID, create_report_data


class FixtureTest(unittest.TestCase):
    """Tests for fixtures."""

    def test_create_report_data(self):
        """Test create report."""
        report_data = create_report_data()
        self.assertEqual(report_data["report_uuid"], REPORT_ID)
        self.assertEqual(report_data["title"], "Title")
        self.assertEqual(report_data["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["name"], "Metric")

    def test_create_report_data_deleted(self):
        """Test create report data for a deleted report."""
        report_data = create_report_data(deleted=True)
        self.assertTrue(report_data["deleted"])
