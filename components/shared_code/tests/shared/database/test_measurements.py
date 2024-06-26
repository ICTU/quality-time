"""Unit tests for the measurements collection."""

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import mongomock

from shared.database.measurements import insert_new_measurement, latest_measurement, latest_successful_measurement
from shared.database.reports import get_reports
from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.model.report import Report
from shared.utils.functions import iso_timestamp

from tests.fixtures import METRIC_ID, METRIC_ID2, create_report
from tests.shared.base import DataModelTestCase

if TYPE_CHECKING:
    from pymongo.database import Database


@patch("shared.model.measurement.iso_timestamp", Mock(return_value=iso_timestamp()))
class MeasurementsTest(DataModelTestCase):
    """Unit test for getting and inserting measurements."""

    def setUp(self) -> None:
        """Set up fixtures for measurements."""
        super().setUp()
        self.database_mock = Mock()
        self.database_mock.measurements.find_one.return_value = None
        self.database_mock.measurements.insert_one = self.insert_one_measurement
        self.metric = Metric(self.DATA_MODEL, {"type": "violations"}, METRIC_ID)
        self.measurements = [
            {"_id": 1, "start": "0", "end": "1", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 2, "start": "3", "end": "4", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 3, "start": "6", "end": "7", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 4, "start": "1", "end": "2", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 5, "start": "4", "end": "5", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 6, "start": "7", "end": "8", "sources": [], "metric_uuid": METRIC_ID2},
        ]
        self.database: Database = mongomock.MongoClient()["quality_time_db"]

    @staticmethod
    def insert_one_measurement(measurement: Measurement) -> None:
        """Mock inserting a measurement into the measurements collection."""
        measurement["_id"] = "measurement_id"

    def test_no_latest_measurement(self):
        """Test no measurements found."""
        self.database_mock.measurements.find_one.return_value = None
        self.assertIsNone(latest_measurement(self.database_mock, self.metric))

    def test_latest_measurement(self):
        """Test a latest measurement is found."""
        self.database_mock.measurements.find_one.return_value = {}
        self.assertEqual(Measurement(self.metric), latest_measurement(self.database_mock, self.metric))

    def test_no_latest_successful_measurement(self):
        """Test no successful measurements found."""
        self.database_mock.measurements.find_one.return_value = None
        self.assertIsNone(latest_successful_measurement(self.database_mock, self.metric))

    def test_latest_successful_measurement(self):
        """Test that a successful measurement is found."""
        self.database_mock.measurements.find_one.return_value = {}
        self.assertEqual(Measurement(self.metric), latest_successful_measurement(self.database_mock, self.metric))

    def test_insert_new_measurement_without_id(self):
        """Test inserting a measurement without id."""
        measurement = Measurement(self.metric)
        inserted_measurement = insert_new_measurement(self.database_mock, measurement)
        self.assertNotIn("_id", inserted_measurement)

    def test_insert_new_measurement_with_id(self):
        """Test inserting a measurement with id."""
        measurement = Measurement(self.metric, {"_id": "measurement_id"})
        inserted_measurement = insert_new_measurement(self.database_mock, measurement)
        self.assertNotIn("_id", inserted_measurement)

    def test_insert_new_measurement_removes_source_parameter_hash_from_previous_measurement(self):
        """Test that inserting a measurement also removes the source parameter hash from the previous measurement."""
        latest_measurement = Measurement(self.metric, {"_id": "measurement_id", "source_parameter_hash": "hash"})
        self.database_mock.measurements.find_one.return_value = latest_measurement
        new_measurement = Measurement(self.metric)
        insert_new_measurement(self.database_mock, new_measurement)
        self.database_mock.measurements.update_one.assert_called_once_with(
            {"_id": "measurement_id"}, {"$unset": {"source_parameter_hash": ""}}
        )

    def test_get_reports(self):
        """Test that the reports are returned."""
        reports = get_reports(self.database)
        self.assertEqual(reports, [])
        self.database["reports"].insert_one(create_report("Current report"))
        self.database["reports"].insert_one(create_report("Previous report", last=False))
        self.database["reports"].insert_one(create_report("Deleted report", deleted=True))
        [report] = get_reports(self.database)
        self.assertEqual(report["title"], "Current report")
        self.assertEqual(report.__class__, Report)
