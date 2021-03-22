"""Unit tests for the measurement routes."""

import unittest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch

from routes.measurement import (
    get_measurements,
    post_measurement,
    set_entity_attribute,
    stream_nr_measurements,
)

from ..fixtures import JOHN, METRIC_ID, REPORT_ID, SOURCE_ID, SOURCE_ID2, SUBJECT_ID, SUBJECT_ID2, create_report


class GetMeasurementsTest(unittest.TestCase):
    """Unit tests for the get measurements route."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
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


@patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("model.measurement.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("model.source.iso_timestamp", new=Mock(return_value="2020-01-01"))
@patch("bottle.request")
class PostMeasurementTests(unittest.TestCase):
    """Unit tests for the post measurement route."""

    def setUp(self):
        """Override to setup a mock database fixture with some content."""
        self.database = Mock()
        self.report = dict(
            _id="id",
            report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID2: {},
                SUBJECT_ID: dict(
                    metrics={
                        METRIC_ID: dict(
                            name="name",
                            type="metric_type",
                            scale="count",
                            addition="sum",
                            direction="<",
                            target="0",
                            near_target="10",
                            debt_target=None,
                            accept_debt=False,
                            tags=[],
                            sources={SOURCE_ID: dict(type="junit")},
                        )
                    }
                ),
            },
        )
        self.database.reports.find.return_value = [self.report]
        self.data_model = dict(
            _id="",
            metrics=dict(metric_type=dict(direction="<", scales=["count"])),
            sources=dict(junit=dict(entities={})),
        )
        self.database.datamodels.find_one.return_value = self.data_model

        def set_measurement_id(measurement):
            """Fake setting a measurement id on the inserted measurement."""
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        self.old_measurement = dict(
            _id="id",
            metric_uuid=METRIC_ID,
            count=dict(status="target_met"),
            sources=[self.source(value="0"), dict(source_uuid=SOURCE_ID2)],
        )
        self.database.measurements.find_one.return_value = self.old_measurement
        self.posted_measurement = dict(metric_uuid=METRIC_ID, sources=[])
        self.new_measurement = dict(
            metric_uuid=METRIC_ID,
            sources=self.posted_measurement["sources"],
            start="2019-01-01",
            end="2019-01-01",
            count=dict(
                value=None,
                status=None,
                status_start="2019-01-01",
                target="0",
                near_target="10",
                debt_target=None,
                direction="<",
            ),
        )

    @staticmethod
    def source(*, source_uuid=SOURCE_ID, value="1", entities=None, entity_user_data=None, connection_error=None):
        """Return a measurement source."""
        return dict(
            source_uuid=source_uuid,
            value=value,
            total=None,
            parse_error=None,
            connection_error=connection_error,
            entities=entities or [],
            entity_user_data=entity_user_data or {},
        )

    def test_first_measurement(self, request):
        """Post the first measurement for a metric."""
        self.database.measurements.find_one.return_value = None
        request.json = self.posted_measurement
        del self.new_measurement["count"]["status_start"]
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_first_measurement_two_scales(self, request):
        """Post the first measurement for a metric with two scales."""
        self.database.measurements.find_one.return_value = None
        self.data_model["metrics"]["metric_type"]["scales"].append("percentage")
        del self.new_measurement["count"]["status_start"]
        request.json = self.posted_measurement
        self.new_measurement["percentage"] = dict(direction="<", status=None, value=None)
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_unchanged_measurement(self, request):
        """Post an unchanged measurement for a metric."""
        self.posted_measurement["sources"] = self.old_measurement["sources"]
        request.json = self.posted_measurement
        self.assertDictEqual(dict(ok=True), post_measurement(self.database))
        self.database.measurements.update_one.assert_called_once()

    def test_changed_measurement_value(self, request):
        """Post a changed measurement for a metric."""
        self.posted_measurement["sources"].append(self.source())
        request.json = self.posted_measurement
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    @patch("server_utilities.functions.datetime", new=Mock(now=Mock(return_value=datetime(2021, 1, 1))))
    def test_changed_measurement_entities(self, request):
        """Post a measurement whose value is the same, but with different entities.

        Entity user data will be changed as follows:
        - Entity data belonging to entities still present is simply copied.
        - Entity data no longer belonging to an entity because the entity disappeared will be marked as orphaned.
        - Entity data that was orphaned recently will still be orphaned.
        - Entity data that was orphaned long ago will be deleted.
        - Entity data that was orphaned, but whose entity reappears, will no longer be orphaned.
        """
        self.old_measurement["count"] = dict(status="near_target_met", status_start="2018-01-01", value="1")
        self.old_measurement["sources"] = [
            self.source(
                entities=[dict(key="a")],
                entity_user_data=dict(
                    a=dict(status="confirmed"),  # Will be newly orphaned
                    b=dict(status="confirmed", orphaned_since="2021-01-01"),  # Will be reunited with its entity
                    c=dict(status="confirmed", orphaned_since="2021-01-01"),  # Will still be orphaned
                    d=dict(status="confirmed", orphaned_since="2020-01-01"),  # Orphaned too long, will be deleted
                ),
            )
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="b")]))
        request.json = self.posted_measurement
        self.new_measurement["count"].update(dict(status="near_target_met", status_start="2018-01-01", value="1"))
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once_with(
            dict(
                metric_uuid=METRIC_ID,
                sources=[
                    self.source(
                        entities=[dict(key="b")],
                        entity_user_data=dict(
                            a=dict(status="confirmed", orphaned_since="2020-01-01"),  # Newly orphaned
                            b=dict(status="confirmed"),  # No longer orphaned
                            c=dict(status="confirmed", orphaned_since="2021-01-01"),  # Still orphaned
                        ),
                    )
                ],
                count=dict(
                    value="1",
                    status="near_target_met",
                    status_start="2018-01-01",
                    direction="<",
                    target="0",
                    near_target="10",
                    debt_target=None,
                ),
                start="2019-01-01",
                end="2019-01-01",
            )
        )

    def test_changed_measurement_entity_key(self, request):
        """Post a measurement whose value and entities are the same, except for a changed entity key."""
        self.old_measurement["sources"] = [
            self.source(entities=[dict(key="a")], entity_user_data=dict(a=dict(status="confirmed")))
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(old_key="a", key="b")]))
        request.json = self.posted_measurement
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once_with(
            dict(
                metric_uuid=METRIC_ID,
                sources=[
                    self.source(
                        entities=[dict(key="b", old_key="a")], entity_user_data=dict(b=dict(status="confirmed"))
                    )
                ],
                count=dict(
                    value="1",
                    status="near_target_met",
                    status_start="2019-01-01",
                    direction="<",
                    target="0",
                    near_target="10",
                    debt_target=None,
                ),
                start="2019-01-01",
                end="2019-01-01",
            )
        )

    def test_ignored_measurement_entities(self, request):
        """Post a measurement where the old one has ignored entities."""
        self.old_measurement["sources"] = [
            self.source(
                entities=[dict(key="entity1")],
                entity_user_data=dict(entity1=dict(status="false_positive", rationale="Rationale")),
            )
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="entity1")]))
        request.json = self.posted_measurement
        self.assertDictEqual(dict(ok=True), post_measurement(self.database))
        self.database.measurements.update_one.assert_called_once_with(
            filter={"_id": "id"}, update={"$set": {"end": "2019-01-01"}}
        )

    def test_ignored_measurement_entities_and_failed_measurement(self, request):
        """Post a measurement where the last successful one has ignored entities."""
        self.database.measurements.find_one.side_effect = [
            dict(
                _id="id1",
                count=dict(status=None, status_start="2018-12-01"),
                sources=[self.source()],
            ),
            dict(
                _id="id2",
                status="target_met",
                sources=[
                    self.source(
                        entities=[dict(key="entity1")],
                        entity_user_data=dict(entity1=dict(status="false_positive", rationale="Rationale")),
                    )
                ],
            ),
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="entity1")]))
        request.json = self.posted_measurement
        self.new_measurement["count"].update(dict(status="target_met", value="0"))
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_all_previous_measurements_were_failed_measurements(self, request):
        """Post a measurement without a last successful one."""
        self.database.measurements.find_one.side_effect = [
            dict(_id="id1", count=dict(status=None), sources=[self.source(connection_error="Error")]),
            None,
        ]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="entity1")]))
        request.json = self.posted_measurement
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_deleted_metric(self, request):
        """Post a measurement for a deleted metric."""
        self.report["subjects"][SUBJECT_ID]["metrics"] = {}
        request.json = self.posted_measurement
        self.assertDictEqual(dict(ok=False), post_measurement(self.database))
        self.database.measurements.update_one.assert_not_called()

    def test_new_source(self, request):
        """Post a measurement for a new source."""
        del self.old_measurement["sources"][0]
        self.posted_measurement["sources"].append(self.source(entities=[dict(key="entity1")]))
        request.json = self.posted_measurement
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_expired_technical_debt(self, request):
        """Test that a new measurement is added when technical debt expires."""
        debt_end_date = date.today() - timedelta(days=1)
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_end_date"] = debt_end_date.isoformat()
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"] = "100"
        self.posted_measurement["sources"].append(self.source())
        self.old_measurement["count"] = dict(
            value="1", status="debt_target_met", target="0", near_target="10", debt_target="100"
        )
        request.json = self.posted_measurement
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_technical_debt_off(self, request):
        """Test that a new measurement is added when technical debt has been turned off."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"] = "100"
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"] = False
        self.posted_measurement["sources"].append(self.source())
        self.old_measurement["count"] = dict(
            value="1", status="debt_target_met", target="0", near_target="10", debt_target="100"
        )
        request.json = self.posted_measurement
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertDictEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()


class SetEntityAttributeTest(unittest.TestCase):
    """Unit tests for the set entity attribute route."""

    def test_set_attribute(self):
        """Test that setting an attribute inserts a new measurement."""
        database = Mock()
        database.sessions.find_one.return_value = JOHN
        measurement = database.measurements.find_one.return_value = dict(
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
                    entities=[dict(key="entity_key", title="entity title")],
                )
            ],
        )
        database.measurements.find.return_value = [measurement]

        def insert_one(new_measurement):
            """Fake setting an id on the inserted measurement."""
            new_measurement["_id"] = "id"

        database.measurements.insert_one = insert_one
        database.reports = Mock()
        database.reports.find.return_value = [create_report()]
        database.datamodels = Mock()
        database.datamodels.find_one.return_value = dict(
            _id=123,
            metrics=dict(metric_type=dict(direction="<", scales=["count"])),
            sources=dict(source_type=dict(entities={})),
        )
        with patch("bottle.request", Mock(json=dict(attribute="value"))):
            measurement = set_entity_attribute(METRIC_ID, SOURCE_ID, "entity_key", "attribute", database)
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual(dict(attribute="value"), entity)
        self.assertEqual(
            dict(
                description="John changed the attribute of 'entity title' from '' to 'value'.",
                email=JOHN["email"],
                uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            ),
            measurement["delta"],
        )


class StreamNrMeasurementsTest(unittest.TestCase):
    """Unit tests for the number of measurements stream."""

    def test_stream(self):
        """Test that the stream returns the number of measurements whenever it changes."""

        def sleep(seconds):
            """Fake the time.sleep method."""
            return seconds

        database = Mock()
        database.measurements.count_documents.side_effect = [42, 42, 42, 43, 43, 43, 43, 43, 43, 43, 43]
        with patch("time.sleep", sleep):
            stream = stream_nr_measurements(database)
            try:
                self.assertEqual("retry: 2000\nid: 0\nevent: init\ndata: 42\n\n", next(stream))
                self.assertEqual("retry: 2000\nid: 1\nevent: delta\ndata: 43\n\n", next(stream))
                self.assertEqual("retry: 2000\nid: 2\nevent: delta\ndata: 43\n\n", next(stream))
            except StopIteration:  # pragma: no cover
                # DeepSource says: calls to next() should be inside try-except block.
                self.fail("Unexpected StopIteration")
