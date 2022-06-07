"""Unit tests for the measurements collection."""

import json
import unittest
from unittest.mock import Mock

from shared.database.measurements import (
    changelog,
    count_measurements,
    insert_new_measurement,
    latest_measurement,
    latest_successful_measurement,
    measurements_by_metric,
    recent_measurements,
    update_measurement_end,
)
from shared.data_model import DATA_MODEL_JSON
from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.utils.functions import iso_timestamp

from ...fixtures import METRIC_ID


class MeasurementsTest(unittest.TestCase):
    """Unit test for getting and inserting measurements."""

    def setUp(self) -> None:
        """Override to create a database fixture."""
        self.database = Mock()
        self.database.measurements.insert_one = self.insert_one_measurement
        self.database.measurements.update_one = self.update_one_measurement
        self.metric = Metric(json.loads(DATA_MODEL_JSON), dict(type="violations"), "metric_uuid")

    @staticmethod
    def insert_one_measurement(measurement):
        """Mock inserting a measurement into the measurements collection."""
        measurement["_id"] = "measurement_id"

    def update_one_measurement(self, **kwargs):
        """Mock updating the end date of a measurement."""
        measurement = Measurement(self.metric, end=kwargs["update"]["$set"]["end"])
        measurement["end"] = iso_timestamp()
        return measurement

    def test_no_latest_measurement(self):
        """Test no measurements found."""
        self.database.measurements.find_one.return_value = None
        self.assertIsNone(latest_measurement(self.database, self.metric))

    def test_latest_measurement(self):
        """Test a latest measurement is found."""
        self.database.measurements.find_one.return_value = {}
        self.assertEqual(Measurement(self.metric), latest_measurement(self.database, self.metric))

    def test_no_latest_successful_measurement(self):
        """Test no measurements found."""
        self.database.measurements.find_one.return_value = None
        self.assertIsNone(latest_successful_measurement(self.database, self.metric))

    def test_latest_successful_measurement(self):
        """Test that a latest successful measurement is found."""
        self.database.measurements.find_one.return_value = {}
        self.assertEqual(Measurement(self.metric), latest_successful_measurement(self.database, self.metric))

    def test_update_measurement_end(self):
        """Test that the end date of the measurement can be updated."""
        measurement = Measurement(self.metric)
        inserted_measurement = update_measurement_end(self.database, measurement)
        self.assertEqual(inserted_measurement, measurement)

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

    def test_changelog(self):
        """Test retrieving the changelog."""
        self.database.measurements.find.return_value = []
        self.assertEqual([], changelog(self.database, 10))

    def test_count_measurements(self):
        """Test counting the measurements."""
        self.database.measurements.estimated_document_count.return_value = 42
        self.assertEqual(42, count_measurements(self.database))

    def test_measurements_by_metric_no_measurements(self):
        """Test that if a metric has no measurements, an empty list is returned."""
        self.database.measurements.find_one.return_value = None
        self.assertEqual([], measurements_by_metric(self.database, METRIC_ID))

    def test_measurements_by_metric_and_by_timestamp(self):
        """Test that if a metric has no measurements within the time period, an empty list is returned."""
        self.database.measurements.find_one.return_value = None
        self.assertEqual(
            [], measurements_by_metric(self.database, METRIC_ID, min_iso_timestamp="2000", max_iso_timestamp="2001")
        )

    def test_measurements_by_metric(self):
        """Test that if a metric has measurements, a list of measurements is returned."""
        measurement = dict(start="2000")
        self.database.measurements.find_one.return_value = measurement
        self.database.measurements.find.return_value = [measurement]
        self.assertEqual(
            [measurement],
            measurements_by_metric(self.database, METRIC_ID, min_iso_timestamp="2000", max_iso_timestamp="2001"),
        )

    def test_no_recent_measurements(self):
        """Test no recent measurements."""
        measurement = dict(metric_uuid=METRIC_ID, start="2000", sources=[])
        self.database.measurements.find.return_value = [measurement]
        self.assertEqual({METRIC_ID: [measurement]}, recent_measurements(self.database, {METRIC_ID: self.metric}))
