"""Unit tests for the changelog routes."""

import unittest
from unittest.mock import Mock

from routes.changelog import (
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

    def test_get_changelog(self):
        """Test that the changelog is returned."""
        report1 = dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"]))
        report2 = dict(timestamp="2", delta=dict(description="delta2", email=JENNY["email"]))
        self.database.reports.find.return_value = [report2, report1]
        self.database.reports_overviews.find.return_value = []
        self.database.measurements.find.return_value = []
        self.assertEqual(
            dict(
                changelog=[
                    dict(delta="delta2", email=JENNY["email"], timestamp="2"),
                    dict(delta="delta1", email=JENNY["email"], timestamp="1"),
                ]
            ),
            get_changelog("10", self.database),
        )

    def test_get_report_changelog(self):
        """Test that the report changelog is returned."""
        report1 = dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"]))
        report2 = dict(timestamp="2", delta=dict(description="delta2", email=JENNY["email"]))
        self.database.reports.find.return_value = [report2, report1]
        self.database.measurements.find.return_value = []
        self.assertEqual(
            dict(
                changelog=[
                    dict(delta="delta2", email=JENNY["email"], timestamp="2"),
                    dict(delta="delta1", email=JENNY["email"], timestamp="1"),
                ]
            ),
            get_report_changelog(REPORT_ID, "10", self.database),
        )

    def test_get_changelog_with_measurements(self):
        """Test that the changelog is returned."""
        report1 = dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"]))
        measurement2 = dict(delta=dict(description="delta2", email=JENNY["email"]), start="2")
        report3 = dict(timestamp="3", delta=dict(description="delta3", email=JENNY["email"]))
        self.database.reports.find.return_value = [report3, report1]
        self.database.measurements.find.return_value = [measurement2]
        self.assertEqual(
            dict(
                changelog=[
                    dict(delta="delta3", email=JENNY["email"], timestamp="3"),
                    dict(delta="delta2", email=JENNY["email"], timestamp="2"),
                    dict(delta="delta1", email=JENNY["email"], timestamp="1"),
                ]
            ),
            get_metric_changelog(METRIC_ID, "10", self.database),
        )

    def test_get_subject_changelog(self):
        """Test that the changelog can be limited to a specific subject."""
        report1 = dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"]))
        report2 = dict(timestamp="2", delta=dict(description="delta2", email=JENNY["email"]))
        self.database.reports.find.return_value = [report2, report1]
        self.database.measurements.find.return_value = []
        self.assertEqual(
            dict(
                changelog=[
                    dict(delta="delta2", email=JENNY["email"], timestamp="2"),
                    dict(delta="delta1", email=JENNY["email"], timestamp="1"),
                ]
            ),
            get_subject_changelog(SUBJECT_ID, "10", self.database),
        )

    def test_get_metric_changelog(self):
        """Test that the changelog can be limited to a specific metric."""
        report1 = dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"]))
        report2 = dict(timestamp="2", delta=dict(description="delta2", email=JENNY["email"]))
        self.database.reports.find.return_value = [report2, report1]
        self.database.measurements.find.return_value = []
        self.assertEqual(
            dict(
                changelog=[
                    dict(delta="delta2", email=JENNY["email"], timestamp="2"),
                    dict(delta="delta1", email=JENNY["email"], timestamp="1"),
                ]
            ),
            get_metric_changelog(METRIC_ID, "10", self.database),
        )

    def test_get_source_changelog(self):
        """Test that the changelog can be limited to a specific source."""
        report1 = dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"]))
        report2 = dict(timestamp="2", delta=dict(description="delta2", email=JENNY["email"]))
        self.database.reports.find.return_value = [report2, report1]
        self.database.measurements.find.return_value = []
        self.assertEqual(
            dict(
                changelog=[
                    dict(delta="delta2", email=JENNY["email"], timestamp="2"),
                    dict(delta="delta1", email=JENNY["email"], timestamp="1"),
                ]
            ),
            get_source_changelog(SOURCE_ID, "10", self.database),
        )

    def test_get_change_log_after_move(self):
        """Test that changelog entries are not repeated after moving items between reports."""
        report1 = dict(timestamp="1", delta=dict(description="delta1", email=JENNY["email"]))
        report2 = dict(timestamp="2", delta=dict(description="delta2", email=JENNY["email"]))
        self.database.reports.find.return_value = [report2, report1]
        self.database.measurements.find.return_value = []
        self.assertEqual(
            dict(
                changelog=[
                    dict(delta="delta2", email=JENNY["email"], timestamp="2"),
                    dict(delta="delta1", email=JENNY["email"], timestamp="1"),
                ]
            ),
            get_subject_changelog(SUBJECT_ID, "10", self.database),
        )
