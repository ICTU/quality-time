"""Unit tests for the measurements collection."""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import mongomock

from shared.database.measurements import (
    get_recent_measurements,
    insert_new_measurement,
    latest_measurement,
    recent_measurements,
)
from shared.database.shared_data import get_reports, get_reports_and_measurements
from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.model.report import Report
from tests.fixtures import METRIC_ID, METRIC_ID2, create_report

from ..base import DataModelTestCase

PATCH_DB_CLIENT = "shared.initialization.database.client"
NEW_REPORT = "New Report"


class MeasurementsTest(DataModelTestCase):
    """Unit test for getting and inserting measurements."""

    def setUp(self) -> None:
        """Setup unittests for measurements"""
        super().setUp()
        self.database = Mock()
        self.database.measurements.insert_one = self.insert_one_measurement
        self.metric = Metric(self.DATA_MODEL, dict(type="violations"), "metric_uuid")
        self.measurements = [
            {"_id": 1, "start": "0", "end": "1", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 2, "start": "3", "end": "4", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 3, "start": "6", "end": "7", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 4, "start": "1", "end": "2", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 5, "start": "4", "end": "5", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 6, "start": "7", "end": "8", "sources": [], "metric_uuid": METRIC_ID2},
        ]

        self.client = mongomock.MongoClient()
        self.now = datetime.now().replace(microsecond=0, tzinfo=timezone.utc).isoformat()
        self.just_now = (datetime.now().replace(microsecond=0, tzinfo=timezone.utc) - timedelta(hours=1)).isoformat()
        self.older = (datetime.now().replace(microsecond=0, tzinfo=timezone.utc) - timedelta(days=1)).isoformat()

    @staticmethod
    def insert_one_measurement(measurement):
        """Mock inserting a measurement into the measurements collection."""
        measurement["_id"] = "measurement_id"

    def test_no_latest_measurement(self):
        """Test no measurements found."""
        self.database.measurements.find_one.return_value = None
        self.assertIsNone(latest_measurement(self.database, self.metric))

    def test_latest_measurement(self):
        """Test a latest measurement is found."""
        self.database.measurements.find_one.return_value = {}
        self.assertEqual(Measurement(self.metric), latest_measurement(self.database, self.metric))

    def test_insert_new_measurement_without_id(self):
        """Test inserting a measurement without id."""
        measurement = Measurement(self.metric)
        inserted_measurement = insert_new_measurement(self.database, measurement)
        self.assertFalse("_id" in inserted_measurement)

    def test_insert_new_measurement_with_id(self):
        """Test inserting a measurement with id."""
        measurement = Measurement(self.metric, {"_id": "measurement_id"})
        inserted_measurement = insert_new_measurement(self.database, measurement)
        self.assertFalse("_id" in inserted_measurement)

    def test_recent_measurements_by_uuid_uuid_filter(self):
        """Test that we get all measurements with all metric ids."""
        self.database.measurements.find.return_value = self.measurements[0:6]
        metric_1 = Metric({}, {}, METRIC_ID)
        metric_2 = Metric({}, {}, METRIC_ID2)
        measurements = recent_measurements(self.database, metrics_dict={METRIC_ID: metric_1, METRIC_ID2: metric_2})
        self.assertEqual(len(measurements), 2)
        self.assertIn(METRIC_ID, measurements)
        self.assertEqual(len(measurements[METRIC_ID]), 3)
        self.assertIn(METRIC_ID2, measurements)
        self.assertEqual(len(measurements[METRIC_ID2]), 3)

    @patch("shared.database.shared_data.get_reports")
    @patch("shared.database.shared_data.get_recent_measurements")
    @patch("shared.database.shared_data.get_metrics_from_reports")
    def test_get_reports_and_measurements(self, fake_metrics, fake_measurements, fake_reports) -> None:
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
            assert reports == []

            self.client["quality_time_db"]["reports"].insert_one(create_report(NEW_REPORT))
            self.client["quality_time_db"]["reports"].insert_one(create_report("Previous Report", last=False))
            self.client["quality_time_db"]["reports"].insert_one(create_report("Deleted Report", deleted="now"))
            [report] = get_reports()
            self.assertEqual(report["title"], NEW_REPORT)
            self.assertEqual(report.__class__, Report)

    def test_get_recent_measurements(self):
        """Test that the recent measurements are returned."""
        with patch(PATCH_DB_CLIENT, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(create_report(NEW_REPORT, metric_id=METRIC_ID))
            reports = get_reports()

            metrics = []
            for report in reports:
                metrics.extend(report.metrics)
            recent_measurements1 = get_recent_measurements(metrics)
            assert not recent_measurements1

            self.client["quality_time_db"]["measurements"].insert_many(self.measurements)

            measurements = get_recent_measurements(metrics)

            self.assertEqual(len(measurements), 2)
            self.assertEqual(measurements[0]["metric_uuid"], METRIC_ID)
            self.assertEqual(measurements[1]["metric_uuid"], METRIC_ID)

    def test_get_recent_measurements_limit(self):
        """Test that the recent measurements are returned."""
        with patch(PATCH_DB_CLIENT, return_value=self.client):
            self.client["quality_time_db"]["reports"].insert_one(create_report(NEW_REPORT, metric_id=METRIC_ID))
            reports = get_reports()

            metrics = []
            for report in reports:
                metrics.extend(report.metrics)

            measurements = [
                dict(
                    metric_uuid=METRIC_ID,
                    end=self.now,
                    start=self.older,
                    count=dict(status="target_not_met", value="0"),
                ),
                dict(
                    metric_uuid=METRIC_ID,
                    end=self.just_now,
                    start=self.just_now,
                    count=dict(status="target_not_met", value="30"),
                ),
                dict(metric_uuid=METRIC_ID, end=self.now, start=self.now, count=dict(status="target_met", value="100")),
            ]

            self.client["quality_time_db"]["measurements"].insert_many(measurements)

            measurements = get_recent_measurements(metrics, limit_per_metric=2)

            self.assertEqual(len(measurements), 2)
            self.assertEqual(measurements[0]["metric_uuid"], METRIC_ID)
            self.assertEqual(measurements[0]["count"]["value"], "100")
            self.assertEqual(measurements[1]["metric_uuid"], METRIC_ID)
            self.assertEqual(measurements[1]["count"]["value"], "30")
