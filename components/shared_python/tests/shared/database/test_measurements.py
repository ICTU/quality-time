"""Unit tests for the measurements collection."""

import json
import unittest
from unittest.mock import Mock

from shared.data_model import DATA_MODEL_JSON
from shared.database.measurements import insert_new_measurement, latest_measurement
from shared.model.measurement import Measurement
from shared.model.metric import Metric


class MeasurementsTest(unittest.TestCase):
    """Unit test for getting and inserting measurements."""

    def setUp(self) -> None:
        """Override to create a database fixture."""
        self.database = Mock()
        self.database.measurements.insert_one = self.insert_one_measurement
        self.metric = Metric(json.loads(DATA_MODEL_JSON), dict(type="violations"), "metric_uuid")

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
