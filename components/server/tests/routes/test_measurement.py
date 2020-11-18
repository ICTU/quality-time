"""Unit tests for the measurement routes."""

import unittest
from datetime import date, timedelta
from unittest.mock import Mock, patch

from routes.measurement import get_measurements, post_measurement, set_entity_attribute, stream_nr_measurements

from ..fixtures import JOHN, METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID, SUBJECT_ID2, create_report


class GetMeasurementsTest(unittest.TestCase):
    """Unit tests for the get measurements route."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()

    def test_get_measurements(self):
        """Tests that the measurements for the requested metric are returned."""
        self.database.measurements.find_one.return_value = dict(start="1")
        self.database.measurements.find.return_value = [dict(start="0"), dict(start="1")]
        self.assertEqual(
            dict(measurements=[dict(start="0"), dict(start="1")]), get_measurements(METRIC_ID, self.database))

    @patch("bottle.request")
    def test_get_old_measurements(self, request):
        """Test that the measurements for the requested metric and report date are returned."""
        self.database.measurements.find_one.return_value = dict(start="1")
        self.database.measurements.find.return_value = [dict(start="0"), dict(start="1")]
        request.query = dict(report_date="2020-08-31T23:59:59.000Z")
        self.assertEqual(
            dict(measurements=[dict(start="0"), dict(start="1")]), get_measurements(METRIC_ID, self.database))

    def test_get_measurements_when_there_are_none(self):
        """Tests that the measurements for the requested metric are returned."""
        self.database.measurements.find_one.return_value = None
        self.assertEqual(dict(measurements=[]), get_measurements(METRIC_ID, self.database))


@patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("bottle.request")
class PostMeasurementTests(unittest.TestCase):
    """Unit tests for the post measurement route."""

    def setUp(self):
        """Override to setup a mock database fixture with some content."""
        self.database = Mock()
        self.report = dict(
            _id="id", report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID2: {},
                SUBJECT_ID: dict(
                    metrics={
                        METRIC_ID: dict(
                            name="name", type="metric_type", scale="count", addition="sum", direction="<", target="0",
                            near_target="10", debt_target=None, accept_debt=False, tags=[],
                            sources={SOURCE_ID: dict(type="junit")})})})
        self.database.reports.find.return_value = [self.report]
        self.database.datamodels.find_one.return_value = dict(
            _id="", metrics=dict(metric_type=dict(direction="<", scales=["count"])),
            sources=dict(junit=dict(entities={})))

        def set_measurement_id(measurement):
            """Fake setting a measurement id on the inserted measurement."""
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        self.database.measurements.update_one = Mock()
        self.sources = []
        self.new_measurement = dict(
            metric_uuid=METRIC_ID, sources=self.sources, start="2019-01-01", end="2019-01-01",
            count=dict(value=None, status=None, target="0", near_target="10", debt_target=None, direction="<"))

    def test_first_measurement(self, request):
        """Post the first measurement for a metric."""
        self.database.measurements.find_one.return_value = None
        self.database.measurements.find.return_value = []
        request.json = dict(metric_uuid=METRIC_ID, sources=[])
        self.assertEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_unchanged_measurement(self, request):
        """Post an unchanged measurement for a metric."""
        self.database.measurements.find_one.return_value = dict(_id="id", sources=[])
        request.json = dict(metric_uuid=METRIC_ID, sources=[])
        self.assertEqual(dict(ok=True), post_measurement(self.database))
        self.database.measurements.update_one.assert_called_once()

    def test_changed_measurement_value(self, request):
        """Post a changed measurement for a metric."""
        measurement = self.database.measurements.find_one.return_value = dict(
            _id="id", metric_uuid=METRIC_ID, status="target_met",
            sources=[dict(source_uuid=SOURCE_ID, value="0", entities=[])])
        self.database.measurements.find.return_value = [measurement]
        self.sources.append(
            dict(source_uuid=SOURCE_ID, value="1", total=None, parse_error=None, connection_error=None, entities=[]))
        request.json = dict(metric_uuid=METRIC_ID, sources=self.sources)
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_changed_measurement_entities(self, request):
        """Post a measurement whose value is the same, but with different entities."""
        measurement = self.database.measurements.find_one.return_value = dict(
            _id="id", metric_uuid=METRIC_ID, status="target_met",
            sources=[
                dict(source_uuid=SOURCE_ID, value="1", entities=[dict(key="a")],
                     entity_user_data=dict(a="attributes"))])
        self.database.measurements.find.return_value = [measurement]
        self.sources.append(
            dict(source_uuid=SOURCE_ID, value="1", total=None, parse_error=None, connection_error=None,
                 entities=[dict(key="b")]))
        request.json = dict(metric_uuid=METRIC_ID, sources=self.sources)
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_changed_measurement_entity_key(self, request):
        """Post a measurement whose value and entities are the same, except for a changed entity key."""
        measurement = self.database.measurements.find_one.return_value = dict(
            _id="id", metric_uuid=METRIC_ID, status="target_met",
            sources=[
                dict(source_uuid=SOURCE_ID, value="1", entities=[dict(key="a")],
                     entity_user_data=dict(a=dict(status="confirmed")))])
        self.database.measurements.find.return_value = [measurement]
        self.sources.append(
            dict(source_uuid=SOURCE_ID, value="1", total=None, parse_error=None, connection_error=None,
                 entities=[dict(old_key="a", key="b")]))
        request.json = dict(metric_uuid=METRIC_ID, sources=self.sources)
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once_with(
            dict(
                metric_uuid=METRIC_ID,
                sources=[
                    dict(source_uuid=SOURCE_ID, value="1", total=None, parse_error=None, connection_error=None,
                         entities=[dict(key="b", old_key="a")], entity_user_data=dict(b=dict(status="confirmed")))],
                count=dict(
                    value="1", status="near_target_met", direction="<", target="0", near_target="10", debt_target=None),
                start="2019-01-01", end="2019-01-01"))

    def test_ignored_measurement_entities(self, request):
        """Post a measurement where the old one has ignored entities."""
        self.database.measurements.find_one.return_value = dict(
            _id="id", status="target_met",
            sources=[
                dict(value="1", parse_error=None, connection_error=None,
                     entity_user_data=dict(entity1=dict(status="false_positive", rationale="Rationale")),
                     entities=[dict(key="entity1")])])
        self.sources.append(dict(value="1", parse_error=None, connection_error=None, entities=[dict(key="entity1")]))
        request.json = dict(metric_uuid=METRIC_ID, sources=self.sources)
        self.assertEqual(dict(ok=True), post_measurement(self.database))
        self.database.measurements.update_one.assert_called_once_with(
            filter={'_id': 'id'}, update={'$set': {'end': '2019-01-01'}})

    def test_ignored_measurement_entities_and_failed_measurement(self, request):
        """Post a measurement where the last successful one has ignored entities."""
        self.database.measurements.find_one.side_effect = [
            dict(
                _id="id1", status=None,
                sources=[
                    dict(source_uuid=SOURCE_ID, value=None, parse_error=None, connection_error="Error", entities=[])]),
            dict(
                _id="id2", status="target_met",
                sources=[
                    dict(source_uuid=SOURCE_ID, value="1", parse_error=None, connection_error=None,
                         entity_user_data=dict(entity1=dict(status="false_positive", rationale="Rationale")),
                         entities=[dict(key="entity1")])])]
        self.sources.append(
            dict(source_uuid=SOURCE_ID, value="1", parse_error=None, connection_error=None,
                 entities=[dict(key="entity1")]))
        request.json = dict(metric_uuid=METRIC_ID, sources=self.sources)
        self.new_measurement["count"].update(dict(status="target_met", value="0"))
        self.assertEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_all_previous_measurements_were_failed_measurements(self, request):
        """Post a measurement without a last successful one."""
        self.database.measurements.find_one.side_effect = [
            dict(
                _id="id1",
                status=None,
                sources=[
                    dict(source_uuid=SOURCE_ID, value=None, parse_error=None, connection_error="Error", entities=[])]),
            None]
        self.sources.append(
            dict(source_uuid=SOURCE_ID, value="1", parse_error=None, connection_error=None,
                 entities=[dict(key="entity1")]))
        request.json = dict(metric_uuid=METRIC_ID, sources=self.sources)
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_deleted_metric(self, request):
        """Post an measurement for a deleted metric."""
        self.database.measurements.find_one.return_value = dict(_id="id", sources=[])
        self.report["subjects"][SUBJECT_ID]["metrics"] = {}
        request.json = dict(metric_uuid=METRIC_ID, sources=[])
        self.assertEqual(dict(ok=False), post_measurement(self.database))
        self.database.measurements.update_one.assert_not_called()

    def test_expired_technical_debt(self, request):
        """Test that a new measurement is added when technical debt expires."""
        debt_end_date = date.today() - timedelta(days=1)
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_end_date"] = debt_end_date.isoformat()
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"] = "100"
        self.sources.append(
            dict(source_uuid=SOURCE_ID, value="1", parse_error=None, connection_error=None, entities=[]))
        self.database.measurements.find_one.return_value = dict(
            _id="id", metric_uuid=METRIC_ID, sources=self.sources,
            count=dict(value="1", status="debt_target_met", target="0", near_target="10", debt_target="100"))
        request.json = dict(metric_uuid=METRIC_ID, sources=self.sources)
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_technical_debt_off(self, request):
        """Test that a new measurement is added when technical debt has been turned off."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["debt_target"] = "100"
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["accept_debt"] = False
        self.sources.append(
            dict(source_uuid=SOURCE_ID, value="1", parse_error=None, connection_error=None, entities=[]))
        self.database.measurements.find_one.return_value = dict(
            _id="id", metric_uuid=METRIC_ID, sources=self.sources,
            count=dict(value="1", status="debt_target_met", target="0", near_target="10", debt_target="100"))
        request.json = dict(metric_uuid=METRIC_ID, sources=self.sources)
        self.new_measurement["count"].update(dict(status="near_target_met", value="1"))
        self.assertEqual(self.new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()


class SetEntityAttributeTest(unittest.TestCase):
    """Unit tests for the set entity attribute route."""

    def test_set_attribute(self):
        """Test that setting an attribute inserts a new measurement."""
        database = Mock()
        database.sessions.find_one.return_value = JOHN
        measurement = database.measurements.find_one.return_value = dict(
            _id="id", metric_uuid=METRIC_ID, status="red",
            sources=[
                dict(
                    source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42", total=None,
                    entities=[dict(key="entity_key", title="entity title")])])
        database.measurements.find.return_value = [measurement]

        def insert_one(new_measurement):
            """Fake setting an id on the inserted measurement."""
            new_measurement["_id"] = "id"

        database.measurements.insert_one = insert_one
        database.reports = Mock()
        database.reports.find.return_value = [create_report()]
        database.datamodels = Mock()
        database.datamodels.find_one.return_value = dict(
            _id=123, metrics=dict(metric_type=dict(direction="<", scales=["count"])),
            sources=dict(source_type=dict(entities={})))
        with patch("bottle.request", Mock(json=dict(attribute="value"))):
            measurement = set_entity_attribute(METRIC_ID, SOURCE_ID, "entity_key", "attribute", database)
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual(dict(attribute="value"), entity)
        self.assertEqual(
            dict(description="John changed the attribute of 'entity title' from '' to 'value'.", email=JOHN["email"],
                 uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID]),
            measurement["delta"])


class StreamNrMeasurementsTest(unittest.TestCase):
    """Unit tests for the number of measurements stream."""

    def test_stream(self):
        """Test that the stream returns the number of measurements whenever it changes."""

        def sleep(seconds):
            """Fake time.sleep()."""
            return seconds

        database = Mock()
        database.measurements.count_documents.side_effect = [42, 42, 42, 43, 43, 43, 43, 43, 43, 43, 43]
        with patch("time.sleep", sleep):
            stream = stream_nr_measurements(database)
            self.assertEqual("retry: 2000\nid: 0\nevent: init\ndata: 42\n\n", next(stream))
            self.assertEqual("retry: 2000\nid: 1\nevent: delta\ndata: 43\n\n", next(stream))
            self.assertEqual("retry: 2000\nid: 2\nevent: delta\ndata: 43\n\n", next(stream))
