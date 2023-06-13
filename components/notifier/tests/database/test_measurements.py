"""Unit tests for the measurements collection."""

import unittest
from datetime import UTC, datetime, timedelta

import mongomock

from shared.database.reports import get_reports

from database.measurements import get_recent_measurements

from tests.fixtures import METRIC_ID, create_report


class MeasurementsTest(unittest.TestCase):
    """Unit tests for getting measurements."""

    def setUp(self) -> None:
        """Set up fixtures for measurements."""
        self.measurements = [
            {"_id": 1, "start": "0", "end": "1", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 2, "start": "3", "end": "4", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 3, "start": "6", "end": "7", "sources": [], "metric_uuid": METRIC_ID},
        ]
        self.database = mongomock.MongoClient()["quality_time_db"]

    def test_get_recent_measurements(self):
        """Test that the recent measurements are returned."""
        self.database["reports"].insert_one(create_report())
        reports = get_reports(self.database)

        metrics = []
        for report in reports:
            metrics.extend(report.metrics)
        recent_measurements1 = get_recent_measurements(self.database, metrics)
        self.assertEqual([], recent_measurements1)

        self.database["measurements"].insert_many(self.measurements)

        measurements = get_recent_measurements(self.database, metrics)

        self.assertEqual(len(measurements), 2)
        self.assertEqual(measurements[0]["metric_uuid"], METRIC_ID)
        self.assertEqual(measurements[1]["metric_uuid"], METRIC_ID)

    def test_get_recent_measurements_limit(self):
        """Test that the recent measurements are returned."""
        self.database["reports"].insert_one(create_report())
        reports = get_reports(self.database)

        metrics = []
        for report in reports:
            metrics.extend(report.metrics)

        now = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
        just_now = (datetime.now(tz=UTC).replace(microsecond=0) - timedelta(hours=1)).isoformat()
        older = (datetime.now(tz=UTC).replace(microsecond=0) - timedelta(days=1)).isoformat()

        measurements = [
            {
                "metric_uuid": METRIC_ID,
                "end": now,
                "start": older,
                "count": {"status": "target_not_met", "value": "0"},
            },
            {
                "metric_uuid": METRIC_ID,
                "end": just_now,
                "start": just_now,
                "count": {"status": "target_not_met", "value": "30"},
            },
            {
                "metric_uuid": METRIC_ID,
                "end": now,
                "start": now,
                "count": {"status": "target_met", "value": "100"},
            },
        ]

        self.database["measurements"].insert_many(measurements)

        measurements = get_recent_measurements(self.database, metrics, limit_per_metric=2)

        self.assertEqual(len(measurements), 2)
        self.assertEqual(measurements[0]["metric_uuid"], METRIC_ID)
        self.assertEqual(measurements[0]["count"]["value"], "100")
        self.assertEqual(measurements[1]["metric_uuid"], METRIC_ID)
        self.assertEqual(measurements[1]["count"]["value"], "30")
