"""Unit tests for the report routes."""

from shared.model.report import Report

from routes import get_reports

from ..base import DataModelTestCase
from ..fixtures import REPORT_ID, create_report


class ReportTest(DataModelTestCase):  # skipcq: PTC-W0046
    """Unit tests for getting reports."""

    def setUp(self):
        """Extend to set up a report."""
        super().setUp()
        self.database.reports.find.return_value = [Report(self.DATA_MODEL, create_report())]
        self.database.measurements.find.return_value = []

    def test_get_report(self):
        """Test that the reports can be retrieved."""
        reports = get_reports(self.database)["reports"]
        self.assertEqual(1, len(reports))
        self.assertEqual(REPORT_ID, reports[0][REPORT_ID])
