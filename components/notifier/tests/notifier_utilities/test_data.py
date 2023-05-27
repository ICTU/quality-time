"""Unit tests for the notifier_utilities.data module."""

import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

import mongomock
from shared.model.report import Report

from notifier_utilities.data import (
    database,
    get_metrics_from_reports,
    get_reports,
    get_reports_and_measurements,
    recent_measurements,
)
from tests.fixtures import METRIC_ID, METRIC_ID2, create_report

PATCH_DB_CLIENT = "notifier_utilities.data.client"
NEW_REPORT = "New Report"


class NotifyUtilitiesTests(unittest.TestCase):
    """Unit tests for the notifier_utilities.data module."""

    def setUp(self) -> None:
        """Define info that is used in multiple tests."""
        self.client = mongomock.MongoClient()
        self.now = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
        self.just_now = (datetime.now(tz=UTC).replace(microsecond=0) - timedelta(hours=1)).isoformat()
        self.older = (datetime.now(tz=UTC).replace(microsecond=0) - timedelta(days=1)).isoformat()

        self.measurements = [
            {
                "metric_uuid": METRIC_ID,
                "end": self.now,
                "start": self.now,
                "count": {"status": "target_not_met", "value": "0"},
            },
            {
                "metric_uuid": METRIC_ID,
                "end": self.just_now,
                "start": self.just_now,
                "count": {"status": "target_met", "value": "10"},
            },
            {
                "metric_uuid": METRIC_ID2,
                "end": self.now,
                "start": self.now,
                "count": {"status": "target_not_met", "value": "0"},
            },
            {
                "metric_uuid": METRIC_ID2,
                "end": self.just_now,
                "start": self.just_now,
                "count": {"status": "target_met", "value": "10"},
            },
        ]

    @patch("notifier_utilities.data.pymongo", return_value=mongomock)
    def test_client(self, client: mongomock) -> None:
        """Test that the client is called."""
        database()
        client.MongoClient.assert_called_once()

    @patch("notifier_utilities.data.get_reports")
    @patch("notifier_utilities.data.recent_measurements")
    @patch("notifier_utilities.data.get_metrics_from_reports")
    def test_get_reports_and_measurements(
        self,
        fake_metrics: Mock,
        fake_measurements: Mock,
        fake_reports: Mock,
    ) -> None:
        """Test that the reports and measurements are returned."""
        with patch(PATCH_DB_CLIENT, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(create_report(NEW_REPORT, metric_id=METRIC_ID))

            self.client["quality_time_db"]["measurements"].insert_many(self.measurements)

            get_reports_and_measurements()
            fake_reports.assert_called_once()
            fake_measurements.assert_called_once()
            fake_metrics.assert_called_once()

    def test_get_reports(self) -> None:
        """Test that the reports are returned."""
        with patch(PATCH_DB_CLIENT, return_value=self.client):
            reports = get_reports()
            self.assertEqual(reports, [])

            self.client["quality_time_db"]["reports"].insert_one(create_report(NEW_REPORT))
            self.client["quality_time_db"]["reports"].insert_one(create_report("Previous Report", last=False))
            self.client["quality_time_db"]["reports"].insert_one(create_report("Deleted Report", deleted="now"))
            [report] = get_reports()
            self.assertEqual(report["title"], NEW_REPORT)
            self.assertEqual(report.__class__, Report)

    def test_recent_measurements(self):
        """Test that the recent measurements are returned."""
        with patch(PATCH_DB_CLIENT, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(create_report(NEW_REPORT, metric_id=METRIC_ID))
            reports = get_reports()

            metrics = []
            for report in reports:
                metrics.extend(report.metrics)

            recent_measurements1 = recent_measurements(*metrics)
            self.assertFalse(recent_measurements1)

            self.client["quality_time_db"]["measurements"].insert_many(self.measurements)

            measurements = recent_measurements(*metrics)

            self.assertEqual(len(measurements), 2)
            self.assertEqual(measurements[0]["metric_uuid"], METRIC_ID)
            self.assertEqual(measurements[1]["metric_uuid"], METRIC_ID)

    def test_recent_measurements_limit(self):
        """Test that the recent measurements are returned."""
        with patch(PATCH_DB_CLIENT, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(create_report(NEW_REPORT, metric_id=METRIC_ID))
            reports = get_reports()

            metrics = []
            for report in reports:
                metrics.extend(report.metrics)

            measurements = [
                {
                    "metric_uuid": METRIC_ID,
                    "end": self.now,
                    "start": self.older,
                    "count": {"status": "target_not_met", "value": "0"},
                },
                {
                    "metric_uuid": METRIC_ID,
                    "end": self.just_now,
                    "start": self.just_now,
                    "count": {"status": "target_not_met", "value": "30"},
                },
                {
                    "metric_uuid": METRIC_ID,
                    "end": self.now,
                    "start": self.now,
                    "count": {"status": "target_met", "value": "100"},
                },
            ]

            self.client["quality_time_db"]["measurements"].insert_many(measurements)

            measurements = recent_measurements(*metrics, limit_per_metric=2)

            self.assertEqual(len(measurements), 2)
            self.assertEqual(measurements[0]["metric_uuid"], METRIC_ID)
            self.assertEqual(measurements[0]["count"]["value"], "100")
            self.assertEqual(measurements[1]["metric_uuid"], METRIC_ID)
            self.assertEqual(measurements[1]["count"]["value"], "30")

    def test_get_metrics_from_reports(self):
        """Test that the metrics are returned."""
        with patch(PATCH_DB_CLIENT, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(create_report(NEW_REPORT, metric_id=METRIC_ID))
            reports = get_reports()
            metrics = get_metrics_from_reports(reports)
            self.assertEqual(metrics[0].uuid, METRIC_ID)
