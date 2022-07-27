"""Unit tests for the report routes."""

import unittest
from unittest.mock import Mock

from shared_data_model import DATA_MODEL
from shared.model.report import Report

from routes import get_report

from ..fixtures import REPORT_ID, create_report


class ReportTest(unittest.TestCase):  # skipcq: PTC-W0046
    """Unit tests for getting reports."""

    def setUp(self):
        """Override to set up a database with a report."""
        self.database = Mock()
        data_model = DATA_MODEL.dict()
        data_model["_id"] = "id"
        self.database.datamodels.find_one.return_value = data_model
        self.database.reports.find.return_value = [Report(data_model, create_report())]
        self.database.measurements.find.return_value = []

    def test_get_report(self):
        """Test that the reports can be retrieved."""
        reports = get_report(self.database)["reports"]
        self.assertEqual(1, len(reports))
        self.assertEqual(REPORT_ID, reports[0][REPORT_ID])
