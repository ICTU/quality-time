"""Unit tests for the measurement routes."""

from unittest.mock import Mock, patch

from routes import get_measurements, set_entity_attribute, stream_nr_measurements

from ..base import DatabaseTestCase, DataModelTestCase
from ..fixtures import JOHN, METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID, create_report


class GetMeasurementsTest(DatabaseTestCase):
    """Unit tests for the get measurements route."""

    def setUp(self):
        """Extend to set up the measurements."""
        super().setUp()
        self.measurements = [dict(start="0"), dict(start="1")]
        self.database.measurements.find_one.return_value = self.measurements[-1]
        self.database.measurements.find.return_value = self.measurements

    def test_get_measurements(self):
        """Tests that the measurements for the requested metric are returned."""
        self.assertEqual(dict(measurements=self.measurements), get_measurements(METRIC_ID, self.database))

    @patch("bottle.request")
    def test_get_old_but_not_new_measurements(self, request):
        """Test that the measurements for the requested metric and report date are returned."""
        database_entries = [dict(start="0"), dict(start="1"), dict(start="2")]

        def find_side_effect(query, projection, sort=None):  # pylint: disable=unused-argument
            """Side effect for mocking the database measurements."""
            min_iso_timestamp = query["end"]["$gt"] if "end" in query else ""
            max_iso_timestamp = query["start"]["$lt"] if "start" in query else ""
            return [
                m
                for m in database_entries
                if (not min_iso_timestamp or m["end"] > min_iso_timestamp)
                and (not max_iso_timestamp or m["start"] < max_iso_timestamp)
            ]

        def find_one_side_effect(query, projection, sort=None):
            """Side effect for mocking the last database measurement."""
            return find_side_effect(query, projection, sort)[-1]

        self.database.measurements.find_one.side_effect = find_one_side_effect
        self.database.measurements.find.side_effect = find_side_effect

        request.query = dict(report_date="2")

        self.assertEqual(
            dict(measurements=[dict(start="0"), dict(start="1")]), get_measurements(METRIC_ID, self.database)
        )

    def test_get_measurements_when_there_are_none(self):
        """Tests that the measurements for the requested metric are returned."""
        self.database.measurements.find_one.return_value = None
        self.assertEqual(dict(measurements=[]), get_measurements(METRIC_ID, self.database))


class SetEntityAttributeTest(DataModelTestCase):
    """Unit tests for the set entity attribute route."""

    def setUp(self):
        """Set up test mocks."""
        super().setUp()
        self.database.sessions.find_one.return_value = JOHN
        self.measurement = self.database.measurements.find_one.return_value = dict(
            _id="id",
            metric_uuid=METRIC_ID,
            status="red",
            sources=[
                dict(
                    source_uuid=SOURCE_ID,
                    parse_error=None,
                    connection_error=None,
                    value="42",
                    total=None,
                    entities=[dict(key="entity_key", title="entity title", other="foo", missing=None)],
                )
            ],
        )
        self.database.measurements.find.return_value = [self.measurement]

        def insert_one(new_measurement):
            """Fake setting an id on the inserted measurement."""
            new_measurement["_id"] = "id"

        self.database.measurements.insert_one = insert_one
        self.database.reports = Mock()
        self.database.reports.find.return_value = [create_report()]

    def test_set_attribute(self):
        """Test that setting an attribute inserts a new measurement."""
        with patch("bottle.request", Mock(json=dict(attribute="value"))):
            measurement = set_entity_attribute(METRIC_ID, SOURCE_ID, "entity_key", "attribute", self.database)
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual(dict(attribute="value"), entity)
        self.assertEqual(
            dict(
                description="John Doe changed the attribute of 'entity title/foo/None' from '' to 'value'.",
                email=JOHN["email"],
                uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            ),
            measurement["delta"],
        )


class StreamNrMeasurementsTest(DatabaseTestCase):
    """Unit tests for the number of measurements stream."""

    def test_stream(self):
        """Test that the stream returns the number of measurements whenever it changes."""

        def sleep(seconds):
            """Fake the time.sleep method."""
            return seconds

        self.database.measurements.estimated_document_count.side_effect = [42, 42, 42, 43, 43, 43, 43, 43, 43, 43, 43]
        with patch("time.sleep", sleep):
            stream = stream_nr_measurements(self.database)
            try:
                self.assertEqual("retry: 2000\nid: 0\nevent: init\ndata: 42\n\n", next(stream))
                self.assertEqual("retry: 2000\nid: 1\nevent: delta\ndata: 43\n\n", next(stream))
                self.assertEqual("retry: 2000\nid: 2\nevent: delta\ndata: 43\n\n", next(stream))
            except StopIteration:  # pragma: no cover
                # DeepSource says: calls to next() should be inside try-except block.
                self.fail("Unexpected StopIteration")
