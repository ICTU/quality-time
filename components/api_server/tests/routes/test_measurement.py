"""Unit tests for the measurement routes."""

from datetime import timedelta
from typing import cast
from unittest.mock import Mock, patch

from shared.model.measurement import Measurement
from shared.utils.date_time import now

from routes import get_metric_measurements, get_measurements, set_entity_attribute, stream_nr_measurements

from tests.base import DatabaseTestCase, DataModelTestCase
from tests.fixtures import JOHN, METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID, create_report


class GetMetricMeasurementsTest(DatabaseTestCase):
    """Unit tests for the get metric measurements route."""

    def setUp(self):
        """Extend to set up the measurements."""
        super().setUp()
        self.measurements = [{"start": "0"}, {"start": "1"}]
        self.database.measurements.find_one.return_value = self.measurements[-1]
        self.database.measurements.find.return_value = self.measurements

    def test_get_measurements(self):
        """Tests that the measurements for the requested metric are returned."""
        self.assertEqual({"measurements": self.measurements}, get_metric_measurements(METRIC_ID, self.database))

    @patch("bottle.request")
    def test_get_old_but_not_new_measurements(self, request):
        """Test that the measurements for the requested metric and report date are returned."""
        database_entries = [{"start": "0"}, {"start": "1"}, {"start": "2"}]

        def find_side_effect(query, projection, sort=None) -> list[dict[str, str]]:  # noqa: ARG001
            """Side effect for mocking the database measurements."""
            min_iso_timestamp = query["end"]["$gte"] if "end" in query else ""
            max_iso_timestamp = query["start"]["$lte"] if "start" in query else ""
            return [
                m
                for m in database_entries
                if (not min_iso_timestamp or m["end"] > min_iso_timestamp)
                and (not max_iso_timestamp or m["start"] < max_iso_timestamp)
            ]

        def find_one_side_effect(query, projection, sort=None) -> dict[str, str]:
            """Side effect for mocking the last database measurement."""
            return find_side_effect(query, projection, sort)[-1]

        self.database.measurements.find_one.side_effect = find_one_side_effect
        self.database.measurements.find.side_effect = find_side_effect

        request.query = {"report_date": "2"}

        self.assertEqual(
            {"measurements": [{"start": "0"}, {"start": "1"}]},
            get_metric_measurements(METRIC_ID, self.database),
        )

    def test_get_measurements_when_there_are_none(self):
        """Tests that the measurements for the requested metric are returned."""
        self.database.measurements.find_one.return_value = None
        self.assertEqual({"measurements": []}, get_metric_measurements(METRIC_ID, self.database))


class GetMeasurementsTest(DataModelTestCase):
    """Unit tests for the get measurements route."""

    def setUp(self):
        """Extend to set up the database contents."""
        super().setUp()
        self.measurement = {
            "_id": "id",
            "metric_uuid": METRIC_ID,
            "count": {"status": "target_not_met"},
            "sources": [{"source_uuid": SOURCE_ID, "parse_error": None, "connection_error": None, "value": "42"}],
        }
        self.database.measurements.find.return_value = [self.measurement]

    def test_get_measurements(self):
        """Test that measurements are returned."""
        self.assertEqual({"measurements": [self.measurement]}, get_measurements(self.database))


class SetEntityAttributeTest(DataModelTestCase):
    """Unit tests for the set entity attribute route."""

    def setUp(self):
        """Set up test mocks."""
        super().setUp()
        self.database.sessions.find_one.return_value = JOHN
        self.measurement = self.database.measurements.find_one.return_value = {
            "_id": "id",
            "metric_uuid": METRIC_ID,
            "status": "red",
            "sources": [
                {
                    "source_uuid": SOURCE_ID,
                    "parse_error": None,
                    "connection_error": None,
                    "value": "42",
                    "total": None,
                    "entities": [{"key": "entity_key", "title": "entity title", "other": "foo", "missing": None}],
                },
            ],
        }
        self.database.measurements.find.return_value = [self.measurement]

        def insert_one(new_measurement) -> None:
            """Fake setting an id on the inserted measurement."""
            new_measurement["_id"] = "id"

        self.database.measurements.insert_one = insert_one
        self.database.reports = Mock()
        self.report = create_report()
        self.database.reports.find.return_value = [self.report]

    def set_entity_attribute(self, attribute: str = "attribute", value: str = "value") -> Measurement:
        """Set the entity attribute and return the new measurement."""
        with patch("bottle.request", Mock(json={attribute: value})):
            return cast(Measurement, set_entity_attribute(METRIC_ID, SOURCE_ID, "entity_key", attribute, self.database))

    def test_set_attribute(self):
        """Test that setting an attribute inserts a new measurement."""
        measurement = self.set_entity_attribute()
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual({"attribute": "value"}, entity)
        self.assertEqual(
            {
                "description": "John Doe changed the attribute of 'entity title/foo/None' from '' to 'value'.",
                "email": JOHN["email"],
                "uuids": [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            },
            measurement["delta"],
        )

    def test_set_status_also_sets_status_end_date_if_status_has_a_desired_response_time(self):
        """Test that setting the status also sets the end date when the desired status resolution has been set."""
        deadline = (now() + timedelta(days=10)).date()
        self.report["desired_response_times"] = {"false_positive": 10}
        measurement = self.set_entity_attribute("status", "false_positive")
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual({"status": "false_positive", "status_end_date": str(deadline)}, entity)
        self.assertEqual(
            {
                "description": "John Doe changed the status of 'entity title/foo/None' from '' to 'false_positive' "
                f"and changed the status end date from 'None' to '{deadline}'.",
                "email": JOHN["email"],
                "uuids": [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            },
            measurement["delta"],
        )

    def test_set_status_does_not_set_the_status_end_date_if_it_is_unchanged(self):
        """Test that setting the status does not set the end date if it hasn't changed."""
        deadline = (now() + timedelta(days=10)).date()
        self.measurement["sources"][0]["entity_user_data"] = {"entity_key": {"status_end_date": str(deadline)}}
        self.report["desired_response_times"] = {"false_positive": 10}
        measurement = self.set_entity_attribute("status", "false_positive")
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual({"status": "false_positive", "status_end_date": str(deadline)}, entity)
        self.assertEqual(
            {
                "description": "John Doe changed the status of 'entity title/foo/None' from '' to 'false_positive'.",
                "email": JOHN["email"],
                "uuids": [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            },
            measurement["delta"],
        )

    def test_set_status_does_not_set_status_end_date_if_desired_response_time_turned_off(self):
        """Test that setting the status does not set the end date if the desired response time has been turned off."""
        self.report["desired_response_times"] = {"false_positive": None}
        measurement = self.set_entity_attribute("status", "false_positive")
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual({"status": "false_positive"}, entity)
        self.assertEqual(
            {
                "description": "John Doe changed the status of 'entity title/foo/None' from '' to 'false_positive'.",
                "email": JOHN["email"],
                "uuids": [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            },
            measurement["delta"],
        )

    def test_set_status_does_not_reset_status_end_date_if_status_is_unconfirmed(self):
        """Test that setting the status to unconfirmed does not reset the end date."""
        measurement = self.set_entity_attribute("status", "unconfirmed")
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual({"status": "unconfirmed"}, entity)
        self.assertEqual(
            {
                "description": "John Doe changed the status of 'entity title/foo/None' from '' to 'unconfirmed'.",
                "email": JOHN["email"],
                "uuids": [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            },
            measurement["delta"],
        )


class StreamNrMeasurementsTest(DatabaseTestCase):
    """Unit tests for the number of measurements stream."""

    def test_stream(self):
        """Test that the stream returns the number of measurements whenever it changes."""

        def sleep(seconds: float) -> float:
            """Fake the time.sleep method."""
            return seconds

        self.database.measurements.estimated_document_count.side_effect = [42, 43, 43, 44]
        with patch("time.sleep", sleep):
            stream = stream_nr_measurements(self.database)
            try:
                self.assertEqual("retry: 2000\nid: 0\nevent: init\ndata: 42\n\n", next(stream))
                self.assertEqual(f"retry: 2000\nid: 1\nevent: flush\ndata: {'.' * 256**2}\n\n", next(stream))
                self.assertEqual("retry: 2000\nid: 2\nevent: delta\ndata: 43\n\n", next(stream))
                self.assertEqual("retry: 2000\nid: 3\nevent: delta\ndata: 43\n\n", next(stream))
                self.assertEqual("retry: 2000\nid: 4\nevent: delta\ndata: 44\n\n", next(stream))
            except StopIteration:  # pragma: no cover
                self.fail("Unexpected StopIteration")
