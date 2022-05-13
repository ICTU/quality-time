"""Unit tests for the report routes."""

import unittest
from unittest.mock import Mock

from shared.model.report import Report

from routes import get_report

from ..fixtures import create_report


class ReportTest(unittest.TestCase):
    """Unit tests for getting reports."""

    def setUp(self):
        """Extend to set up a database with a report and a user session."""
        self.database = Mock()
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            metrics=dict(metric_type={}),
        )
        self.database.measurements.find.return_value = []
        self.report = Report(self.database.datamodels.find_one(), create_report())
        self.database.reports.find.return_value = [self.report]

    def test_get_all_reports(self):
        """Test that all reports can be retrieved."""
        self.assertEqual(1, len(get_report(self.database)["reports"]))
