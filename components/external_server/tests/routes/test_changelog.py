"""Unit tests for the changelog routes."""

import unittest
from unittest.mock import Mock

from routes import (
    get_changelog,
    get_metric_changelog,
    get_report_changelog,
    get_source_changelog,
    get_subject_changelog,
)

from ..fixtures import JENNY, METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID


class ChangeLogTest(unittest.TestCase):
    """Unit tests for getting the changelog."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()
        self.database.sessions.find_one.return_value = JENNY
        self.database.reports_overviews.find.return_value = []
        self.database.reports.find.return_value = [
            dict(timestamp="2", delta=dict(description="delta2", email=JENNY["email"])),
            dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"])),
        ]
        self.database.measurements.find.return_value = []
        self.expected_changelog = dict(
            changelog=[
                dict(delta="delta2", email=JENNY["email"], timestamp="2"),
                dict(delta="delta1", email=JENNY["email"], timestamp="1"),
            ]
        )

    def test_get_changelog(self):
        """Test that the changelog is returned."""
        self.assertEqual(self.expected_changelog, get_changelog("10", self.database))

    def test_get_report_changelog(self):
        """Test that the report changelog is returned."""
        self.assertEqual(self.expected_changelog, get_report_changelog(REPORT_ID, "10", self.database))

    def test_get_changelog_with_measurements(self):
        """Test that the changelog is returned."""
        self.database.measurements.find.return_value = [
            dict(delta=dict(description="delta3", email=JENNY["email"]), start="3")
        ]
        self.expected_changelog["changelog"].insert(0, dict(delta="delta3", email=JENNY["email"], timestamp="3"))
        self.assertEqual(self.expected_changelog, get_metric_changelog(METRIC_ID, "10", self.database))

    def test_get_subject_changelog(self):
        """Test that the changelog can be limited to a specific subject."""
        self.assertEqual(self.expected_changelog, get_subject_changelog(SUBJECT_ID, "10", self.database))

    def test_get_metric_changelog(self):
        """Test that the changelog can be limited to a specific metric."""
        self.assertEqual(self.expected_changelog, get_metric_changelog(METRIC_ID, "10", self.database))

    def test_get_source_changelog(self):
        """Test that the changelog can be limited to a specific source."""
        self.assertEqual(self.expected_changelog, get_source_changelog(SOURCE_ID, "10", self.database))

    def test_get_moved_item_changelog(self):
        """Test that the changelog does not contain the moved item twice."""
        self.database.reports.find.return_value = [
            dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"])),
            dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"])),
        ]
        expected_changelog = dict(changelog=[dict(delta="delta1", email=JENNY["email"], timestamp="1")])
        self.assertEqual(expected_changelog, get_changelog("10", self.database))
