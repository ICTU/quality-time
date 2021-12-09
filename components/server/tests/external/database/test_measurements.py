"""Test the measurements collection."""

import unittest
from unittest.mock import Mock

from external.database.measurements import (
    measurements_by_metric,
    recent_measurements,
)
from external.model.metric import Metric

from ..fixtures import METRIC_ID, METRIC_ID2, METRIC_ID3


class MeasurementsByMetricTest(unittest.TestCase):
    """Unittests for querying measurements by one or more metric."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.measurements = [
            {"_id": 1, "start": "0", "end": "1", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 2, "start": "3", "end": "4", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 3, "start": "6", "end": "7", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 4, "start": "1", "end": "2", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 5, "start": "4", "end": "5", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 6, "start": "7", "end": "8", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 7, "start": "2", "end": "3", "sources": [], "metric_uuid": METRIC_ID3},
            {"_id": 8, "start": "5", "end": "6", "sources": [], "metric_uuid": METRIC_ID3},
            {"_id": 9, "start": "8", "end": "9", "sources": [], "metric_uuid": METRIC_ID3},
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
