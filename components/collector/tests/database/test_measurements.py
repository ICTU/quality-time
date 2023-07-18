"""Test measurement collection."""

import unittest

import mongomock

from database.measurements import create_measurement

from tests.fixtures import METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID, create_report


class TestMeasurements(unittest.TestCase):
    """Unit tests for the measurements collection."""

    def setUp(self) -> None:
        """Set up fixtures."""
        self.measurement_data = {
            "start": "2023-07-19T16:50:47+00:000",
            "end": "2023-07-19T16:50:47+00:001",
            "has_error": False,
            "sources": [
                {
                    "type": "sonarqube",
                    "source_uuid": SOURCE_ID,
                    "name": "Source",
                    "parameters": {"url": "https://url", "password": "password"},
                    "parse_error": None,
                    "connection_error": None,
                    "value": "10",
                    "total": "100",
                    "entities": [{"key": "key", "first_seen": "2023-07-18"}],
                },
            ],
            "metric_uuid": METRIC_ID,
            "report_uuid": REPORT_ID,
        }
        self.client: mongomock.MongoClient = mongomock.MongoClient()
        self.database = self.client["quality_time_db"]

    def test_create_measurement_without_latest_measurement(self):
        """Test that create_measurement without a latest measurement inserts a new measurement."""
        self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
        create_measurement(self.database, self.measurement_data)
        self.assertEqual(1, len(list(self.database.measurements.find())))

    def test_create_measurement_with_latest_measurement(self):
        """Test that create_measurement with a latest measurement inserts a new measurement."""
        self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
        self.database["measurements"].insert_one(
            {
                "metric_uuid": METRIC_ID,
                "sources": [
                    {"source_uuid": SOURCE_ID, "parse_error": None, "connection_error": None, "value": "42"},
                ],
            },
        )
        create_measurement(self.database, self.measurement_data)
        self.assertEqual(2, len(list(self.database.measurements.find())))

    def test_create_measurement_with_no_latest_metric(self):
        """Test that create_measurement does not insert new measurement when the metric does not exist."""
        create_measurement(self.database, self.measurement_data)
        self.assertEqual(0, len(list(self.database.measurements.find())))

    def test_create_measurement_without_source(self):
        """Test that a new measurement is not created if the sources used for the measurement no longer exist."""
        report = create_report(report_uuid=REPORT_ID)
        del report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        self.database["reports"].insert_one(report)
        create_measurement(self.database, self.measurement_data)
        self.assertEqual(0, len(list(self.database.measurements.find())))

    def test_create_measurement_when_its_equal(self):
        """Test that create_measurement with equal measurement does not insert new measurement."""
        self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
        create_measurement(self.database, self.measurement_data)
        create_measurement(self.database, self.measurement_data)
        self.assertEqual(1, len(list(self.database.measurements.find())))

    def test_copy_first_seen_timestamps(self):
        """Test that the first seen timestamps are copied from the latest successful measurement."""
        self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
        create_measurement(self.database, self.measurement_data)
        self.measurement_data["sources"][0]["entities"][0]["first_seen"] = "2023-07-19"
        create_measurement(self.database, self.measurement_data)
        self.assertEqual(
            "2023-07-18",
            next(self.database.measurements.find())["sources"][0]["entities"][0]["first_seen"],
        )
