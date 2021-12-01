"""Test the measurements collection."""

import unittest
from unittest.mock import Mock

from database.measurements import (
    latest_measurements_by_metric_uuid,
    measurements_by_metric,
    recent_measurements_by_metric_uuid,
)

from ..fixtures import METRIC_ID, METRIC_ID2, METRIC_ID3


class MeasurementsByMetricTest(unittest.TestCase):
    """Unittests for querying measurements by one or more metric."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.measurements = [
            {"_id": 1, "start": "0", "end": "1", "metric_uuid": METRIC_ID},
            {"_id": 2, "start": "3", "end": "4", "metric_uuid": METRIC_ID},
            {"_id": 3, "start": "6", "end": "7", "metric_uuid": METRIC_ID},
            {"_id": 4, "start": "1", "end": "2", "metric_uuid": METRIC_ID2},
            {"_id": 5, "start": "4", "end": "5", "metric_uuid": METRIC_ID2},
            {"_id": 6, "start": "7", "end": "8", "metric_uuid": METRIC_ID2},
            {"_id": 7, "start": "2", "end": "3", "metric_uuid": METRIC_ID3},
            {"_id": 8, "start": "5", "end": "6", "metric_uuid": METRIC_ID3},
            {"_id": 9, "start": "8", "end": "9", "metric_uuid": METRIC_ID3},
        ]
        self.database.measurements.aggregate.return_value = []

    def test_get_from_one_metric(self):
        """Test that we get all three measurement fields."""
        self.database.measurements.find_one.return_value = self.measurements[0]
        self.database.measurements.find.return_value = self.measurements[0:3]
        measurements = measurements_by_metric(self.database, METRIC_ID)
        self.assertEqual(len(measurements), 3)
        for measurement in measurements:
            self.assertEqual(measurement["metric_uuid"], METRIC_ID)

    def test_get_from_multiple_metric(self):
        """Test that we get all three measurement fields."""
        self.database.measurements.find_one.return_value = self.measurements[0]
        self.database.measurements.find.return_value = self.measurements[0:6]
        measurements = measurements_by_metric(self.database, *[METRIC_ID, METRIC_ID2])
        self.assertEqual(len(measurements), 6)
        for measurement in measurements:
            self.assertIn(measurement["metric_uuid"], [METRIC_ID, METRIC_ID2])

    def test_get_timestamp_restriction(self):
        """Test that we get all three measurement fields."""
        self.database.measurements.find_one.return_value = self.measurements[0]
        self.database.measurements.find.return_value = self.measurements[0:2]
        measurements = measurements_by_metric(self.database, METRIC_ID, min_iso_timestamp="0.5", max_iso_timestamp="4")
        self.assertEqual(len(measurements), 2)
        for measurement in measurements:
            self.assertEqual(measurement["metric_uuid"], METRIC_ID)
            self.assertIn(measurement["start"], ["0", "3"])

    def test_recent_measurements_by_uuid(self):
        """Test that we get all measurements with all metric ids."""
        self.database.measurements.find.return_value = self.measurements
        recent_measurements = recent_measurements_by_metric_uuid(dict(scales=["count"]), self.database)
        self.assertEqual(len(recent_measurements), 3)
        self.assertIn(METRIC_ID, recent_measurements)
        self.assertEqual(len(recent_measurements[METRIC_ID]), 3)
        self.assertIn(METRIC_ID2, recent_measurements)
        self.assertEqual(len(recent_measurements[METRIC_ID2]), 3)
        self.assertIn(METRIC_ID3, recent_measurements)
        self.assertEqual(len(recent_measurements[METRIC_ID3]), 3)

    def test_recent_measurements_by_uuid_uuid_filter(self):
        """Test that we get all measurements with all metric ids."""
        self.database.measurements.find.return_value = self.measurements[0:6]
        recent_measurements = recent_measurements_by_metric_uuid(
            dict(scales=["count"]), self.database, metric_uuids=[METRIC_ID, METRIC_ID2]
        )
        self.assertEqual(len(recent_measurements), 2)
        self.assertIn(METRIC_ID, recent_measurements)
        self.assertEqual(len(recent_measurements[METRIC_ID]), 3)
        self.assertIn(METRIC_ID2, recent_measurements)
        self.assertEqual(len(recent_measurements[METRIC_ID2]), 3)

    def test_latest_measurements_by_uuid_uuid_filter(self):
        """Test that we get all measurements with all metric ids."""
        self.database.measurements.find.return_value = [self.measurements[2], self.measurements[5]]
        latest_measurements = latest_measurements_by_metric_uuid(
            self.database, "", metric_uuids=[METRIC_ID, METRIC_ID2]
        )
        self.assertEqual(len(latest_measurements), 2)
        self.assertIn(METRIC_ID, latest_measurements)
        self.assertEqual(latest_measurements[METRIC_ID]["start"], "6")
        self.assertIn(METRIC_ID2, latest_measurements)
        self.assertEqual(latest_measurements[METRIC_ID2]["start"], "7")
