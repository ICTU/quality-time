"""Unit tests for getting reports from the database."""

import unittest

import mongomock

from database.reports import get_reports_and_measurements

from tests.fixtures import METRIC_ID, create_report


class ReportsTest(unittest.TestCase):
    """Unit tests for getting information from the database."""

    def setUp(self) -> None:
        """Set up the database."""
        self.measurements = [
            {"_id": 1, "start": "0", "end": "1", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 2, "start": "3", "end": "4", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 3, "start": "6", "end": "7", "sources": [], "metric_uuid": METRIC_ID},
        ]
        self.database = mongomock.MongoClient()["quality_time_db"]

    def test_get_reports_and_measurements(self):
        """Test that the reports and latest two measurements are returned."""
        report = create_report()
        self.database["reports"].insert_one(report)
        self.database["measurements"].insert_many(self.measurements)
        reports, measurements = get_reports_and_measurements(self.database)
        self.assertEqual(report["report_uuid"], reports[0]["report_uuid"])
        self.assertEqual(2, len(measurements))
