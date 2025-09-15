"""Unit tests for the measurements collection."""

from unittest.mock import Mock

from shared.database.measurements import insert_new_measurement, latest_measurement
from shared.model.measurement import Measurement
from shared.model.metric import Metric

from tests.fixtures import METRIC_ID
from tests.shared.base import DataModelTestCase


class MeasurementsTestCase(DataModelTestCase):
    """Base class for unit tests for retrieving measurements from and inserting into the database."""

    def setUp(self) -> None:
        """Set up fixtures for measurements."""
        super().setUp()
        self.database = Mock()
        self.database.measurements.find_one.return_value = None
        self.metric = Metric(self.DATA_MODEL, {"type": "violations"}, METRIC_ID)


class LatestMeasurementsTest(MeasurementsTestCase):
    """Unit test for retrieving the latest measurement from the database."""

    def test_no_latest_measurement(self):
        """Test no measurements found."""
        self.assertIsNone(latest_measurement(self.database, self.metric))

    def test_latest_measurement(self):
        """Test a latest measurement is found."""
        self.database.measurements.find_one.return_value = {}
        self.assertEqual(Measurement(self.metric), latest_measurement(self.database, self.metric))

    def test_no_latest_successful_measurement(self):
        """Test no successful measurements found."""
        self.assertIsNone(latest_measurement(self.database, self.metric, skip_measurements_with_error=True))

    def test_latest_successful_measurement(self):
        """Test that a successful measurement is found."""
        self.database.measurements.find_one.return_value = {}
        self.assertEqual(
            Measurement(self.metric),
            latest_measurement(self.database, self.metric, skip_measurements_with_error=True),
        )


class InsertNewMeasurementsTest(MeasurementsTestCase):
    """Unit test for inserting measurements into the database."""

    def setUp(self) -> None:
        """Set up fixtures for measurements."""
        super().setUp()
        self.database.measurements.insert_one = self.insert_one_measurement

    @staticmethod
    def insert_one_measurement(measurement: Measurement) -> None:
        """Mock inserting a measurement into the measurements collection."""
        measurement["_id"] = "measurement_id"

    def test_insert_new_measurement_without_id(self):
        """Test inserting a measurement without id."""
        measurement = Measurement(self.metric)
        inserted_measurement = insert_new_measurement(self.database, measurement)
        self.assertNotIn("_id", inserted_measurement)

    def test_insert_new_measurement_with_id(self):
        """Test inserting a measurement with id."""
        measurement = Measurement(self.metric, {"_id": "measurement_id"})
        inserted_measurement = insert_new_measurement(self.database, measurement)
        self.assertNotIn("_id", inserted_measurement)

    def test_insert_new_measurement_removes_source_parameter_hash_from_previous_measurement(self):
        """Test that inserting a measurement also removes the source parameter hash from the previous measurement."""
        latest_measurement = Measurement(self.metric, {"_id": "measurement_id", "source_parameter_hash": "hash"})
        self.database.measurements.find_one.return_value = latest_measurement
        new_measurement = Measurement(self.metric)
        insert_new_measurement(self.database, new_measurement)
        self.database.measurements.update_one.assert_called_once_with(
            {"_id": "measurement_id"}, {"$unset": {"source_parameter_hash": ""}}
        )
