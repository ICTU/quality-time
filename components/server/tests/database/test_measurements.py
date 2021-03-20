"""Test the measurements collection."""

import unittest
from unittest.mock import Mock

from database.measurements import measurements_by_metric

from ..fixtures import METRIC_ID, METRIC_ID2, METRIC_ID3


class MeasurementsByMetricTest(unittest.TestCase):
    """Unittests for querying measurements by one or more metric."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        measurements = [
            {"start": "0", "end": "1", "metric_uuid": METRIC_ID},
            {"start": "3", "end": "4", "metric_uuid": METRIC_ID},
            {"start": "6", "end": "7", "metric_uuid": METRIC_ID},
            {"start": "1", "end": "2", "metric_uuid": METRIC_ID2},
            {"start": "4", "end": "5", "metric_uuid": METRIC_ID2},
            {"start": "7", "end": "8", "metric_uuid": METRIC_ID2},
            {"start": "2", "end": "3", "metric_uuid": METRIC_ID3},
            {"start": "5", "end": "6", "metric_uuid": METRIC_ID3},
            {"start": "8", "end": "9", "metric_uuid": METRIC_ID3},
        ]

        def find_one_side_effect(query, projection, sort=None):
            """Side effect for mocking the database measurements."""
            return find_side_effect(query, projection, sort)[-1]

        def find_side_effect(query, projection, sort=None):  # pylint: disable=unused-argument
            """Side effect for mocking the last database measurement."""
            metric_uuids = query["metric_uuid"]["$in"]
            min_iso_timestamp = query["end"]["$gt"] if "end" in query else ""
            max_iso_timestamp = query["start"]["$lt"] if "start" in query else ""
            return [
                m
                for m in measurements
                if m["metric_uuid"] in metric_uuids
                and (not min_iso_timestamp or m["end"] > min_iso_timestamp)
                and (not max_iso_timestamp or m["start"] < max_iso_timestamp)
            ]

        self.database.measurements.find_one.side_effect = find_one_side_effect
        self.database.measurements.find.side_effect = find_side_effect

    def test_get_from_one_metric(self):
        """Test that we get all three measurement fields."""
        measurements = measurements_by_metric(self.database, METRIC_ID)
        self.assertEqual(len(measurements), 3)
        for measurement in measurements:
            self.assertEqual(measurement["metric_uuid"], METRIC_ID)

    def test_get_from_multiple_metric(self):
        """Test that we get all three measurement fields."""
        measurements = measurements_by_metric(self.database, *[METRIC_ID, METRIC_ID2])
        self.assertEqual(len(measurements), 6)
        for measurement in measurements:
            self.assertIn(measurement["metric_uuid"], [METRIC_ID, METRIC_ID2])

    def test_get_timestamp_restriction(self):
        """Test that we get all three measurement fields."""
        measurements = measurements_by_metric(self.database, METRIC_ID, min_iso_timestamp="0.5", max_iso_timestamp="4")
        self.assertEqual(len(measurements), 2)
        for measurement in measurements:
            self.assertEqual(measurement["metric_uuid"], METRIC_ID)
            self.assertIn(measurement["start"], ["0", "3"])
