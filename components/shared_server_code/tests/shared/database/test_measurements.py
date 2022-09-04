"""Unit tests for the measurements collection."""

import unittest
from unittest.mock import Mock

from shared_data_model import DATA_MODEL

from shared.database.measurements import insert_new_measurement, latest_measurement, recent_measurements
from shared.model.measurement import Measurement
from shared.model.metric import Metric

from tests.fixtures import METRIC_ID, METRIC_ID2


class MeasurementsTest(unittest.TestCase):
    """Unit test for getting and inserting measurements."""

    @classmethod
    def setUpClass(cls) -> None:
        """Override to prepare the data model."""
        cls.data_model = DATA_MODEL.dict(exclude_none=True)

    def setUp(self) -> None:
        """Override to create a database fixture."""
        self.database = Mock()
        self.database.measurements.insert_one = self.insert_one_measurement
        self.metric = Metric(self.data_model, dict(type="violations"), "metric_uuid")
        self.measurements = [
            {"_id": 1, "start": "0", "end": "1", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 2, "start": "3", "end": "4", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 3, "start": "6", "end": "7", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 4, "start": "1", "end": "2", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 5, "start": "4", "end": "5", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 6, "start": "7", "end": "8", "sources": [], "metric_uuid": METRIC_ID2},
        ]

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
