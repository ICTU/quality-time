"""Unit tests for the measurement routes."""

import unittest
from unittest.mock import Mock, patch

from routes.measurement import get_measurements, post_measurement, set_entity_attribute, stream_nr_measurements
from .fixtures import create_report, METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID, SUBJECT_ID2


class GetMeasurementsTest(unittest.TestCase):
    """Unit tests for the get measurements route."""

    def test_get_measurements(self):
        """Tests that the measurements for the requested metric are returned."""
        database = Mock()
        database.measurements.find.return_value = [dict(_id="id")]
        self.assertEqual(dict(measurements=[dict(_id="id")]), get_measurements(METRIC_ID, database))


@patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("bottle.request")
class PostMeasurementTests(unittest.TestCase):
    """Unit tests for the post measurement route."""

    def setUp(self):
        self.database = Mock()
        report = dict(
            _id="id", report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID2: dict(),
                SUBJECT_ID: dict(
                    metrics={
                        METRIC_ID: dict(
                            name="name", type="metric_type", scale="count", addition="sum", direction="<", target="0",
                            near_target="10", debt_target=None, accept_debt=False, tags=[],
                            sources={SOURCE_ID: dict()})})})
        self.database.reports.find_one.return_value = report
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.datamodels.find_one.return_value = dict(
            _id="", metrics=dict(metric_type=dict(direction="<", scales=["count"])))

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        self.database.measurements.update_one = Mock()

    def test_first_measurement(self, request):
        """Post the first measurement for a metric."""
        self.database.measurements.find_one.return_value = None
        self.database.measurements.find.return_value = []
        request.json = dict(metric_uuid=METRIC_ID, sources=[])
        new_measurement = dict(
            _id="measurement_id", metric_uuid=METRIC_ID, sources=[],
            count=dict(value=None, status=None), start="2019-01-01", end="2019-01-01", last=True)
        self.assertEqual(new_measurement, post_measurement(self.database))
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
            _id="id", metric_uuid=METRIC_ID, status="target_met", last=True, sources=[dict(value="0", entities=[])])
        self.database.measurements.find.return_value = [measurement]
        sources = [dict(value="1", total=None, parse_error=None, connection_error=None, entities=[])]
        request.json = dict(metric_uuid=METRIC_ID, sources=sources)
        new_measurement = dict(
            _id="measurement_id", metric_uuid=METRIC_ID, last=True,
            count=dict(status="near_target_met", value="1"), start="2019-01-01", end="2019-01-01", sources=sources)
        self.assertEqual(new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_changed_measurement_entities(self, request):
        """Post a measurement whose value is the same, but with different entities."""
        measurement = self.database.measurements.find_one.return_value = dict(
            _id="id", metric_uuid=METRIC_ID, status="target_met", last=True,
            sources=[dict(value="1", entities=[dict(key="a")], entity_user_data=dict(a="attributes"))])
        self.database.measurements.find.return_value = [measurement]
        sources = [dict(value="1", total=None, parse_error=None, connection_error=None, entities=[dict(key="b")])]
        request.json = dict(metric_uuid=METRIC_ID, sources=sources)
        new_measurement = dict(
            _id="measurement_id", metric_uuid=METRIC_ID, last=True,
            count=dict(status="near_target_met", value="1"), start="2019-01-01", end="2019-01-01", sources=sources)
        self.assertEqual(new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_ignored_measurement_entities(self, request):
        """Post a measurement where the old one has ignored entities."""
        self.database.measurements.find_one.return_value = dict(
            _id="id", status="target_met",
            sources=[
                dict(value="1", parse_error=None, connection_error=None,
                     entity_user_data=dict(entity1=dict(status="false_positive", rationale="Rationale")),
                     entities=[dict(key="entity1")])])
        sources = [dict(value="1", parse_error=None, connection_error=None, entities=[dict(key="entity1")])]
        request.json = dict(metric_uuid=METRIC_ID, sources=sources)
        self.assertEqual(dict(ok=True), post_measurement(self.database))
        self.database.measurements.update_one.assert_called_once_with(
            filter={'_id': 'id'}, update={'$set': {'end': '2019-01-01', 'last': True}})


class SetEntityAttributeTest(unittest.TestCase):
    """Unit tests for the set entity attribute route."""
    def test_set_attribute(self):
        """Test that setting an attribute inserts a new measurement."""
        database = Mock()
        database.sessions.find_one.return_value = dict(user="John")
        measurement = database.measurements.find_one.return_value = dict(
            _id="id", metric_uuid=METRIC_ID, status="red",
            sources=[
                dict(
                    source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42", total=None,
                    entities=[dict(key="entity_key", title="entity title")])])
        database.measurements.find.return_value = [measurement]

        def insert_one(new_measurement):
            new_measurement["_id"] = "id"

        database.measurements.insert_one = insert_one
        database.reports = Mock()
        database.reports.distinct.return_value = [REPORT_ID]
        database.reports.find_one.return_value = dict(
            _id="id", report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID: dict(
                    metrics={
                        METRIC_ID: dict(
                            type="metric_type", target="0", near_target="10", debt_target="0", accept_debt=False,
                            scale="count", addition="sum", direction="<", tags=[])})})
        database.reports.find_one.return_value = create_report()
        database.datamodels = Mock()
        database.datamodels.find_one.return_value = dict(
            _id=123, metrics=dict(metric_type=dict(direction="<", scales=["count"])))
        with patch("bottle.request", Mock(json=dict(attribute="value"))):
            measurement = set_entity_attribute(
                METRIC_ID, SOURCE_ID, "entity_key", "attribute", database)
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual(dict(attribute="value"), entity)
        self.assertEqual("John changed the attribute of 'entity title' from '' to 'value'.", measurement["delta"])


class StreamNrMeasurementsTest(unittest.TestCase):
    """Unit tests for the number of measurements stream."""

    def test_stream(self):
        """Test that the stream returns the number of measurements whenever it changes."""
        def sleep(seconds):
            return seconds
        database = Mock()
        database.measurements.count_documents.side_effect = [42, 42, 42, 43, 43, 43, 43, 43, 43, 43, 43]
        with patch("time.sleep", sleep):
            stream = stream_nr_measurements(database)
            self.assertEqual("retry: 2000\nid: 0\nevent: init\ndata: 42\n\n", next(stream))
            self.assertEqual("retry: 2000\nid: 1\nevent: delta\ndata: 43\n\n", next(stream))
            self.assertEqual("retry: 2000\nid: 2\nevent: delta\ndata: 43\n\n", next(stream))
