"""Unit tests for the measurement routes."""

import unittest
from unittest.mock import Mock, patch

from src.routes.measurement import get_measurements, post_measurement, set_entity_attribute, stream_nr_measurements


class GetMeasurementsTest(unittest.TestCase):
    """Unit tests for the get measurements route."""

    def test_get_measurements(self):
        """Tests that the measurements for the requested metric are returned."""
        database = Mock()
        database.measurements.find.return_value = [dict(_id="id")]
        self.assertEqual(dict(measurements=[dict(_id="id")]), get_measurements("metric_uuid", database))


@patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("bottle.request")
class PostMeasurementTests(unittest.TestCase):
    """Unit tests for the post measurement route."""

    def setUp(self):
        self.database = Mock()
        report = dict(
            _id="id", report_uuid="report_uuid",
            subjects=dict(
                other_subject=dict(),
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            name="name", type="metric_type", addition="sum", target="0", near_target="10",
                            debt_target=None, accept_debt=False, tags=[], sources=dict(source_uuid=dict()))))))
        self.database.reports.find_one.return_value = report
        self.database.reports.distinct.return_value = ["report_uuid"]
        self.database.datamodels.find_one.return_value = dict(_id="", metrics=dict(metric_type=dict(direction="≦")))

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        self.database.measurements.update_one = Mock()

    def test_first_measurement(self, request):
        """Post the first measurement for a metric."""
        self.database.measurements.find_one.return_value = None
        request.json = dict(report_uuid="report_uuid", metric_uuid="metric_uuid", sources=[])
        new_measurement = dict(
            _id="measurement_id", report_uuid="report_uuid", metric_uuid="metric_uuid", sources=[], value=None,
            status=None, start="2019-01-01", end="2019-01-01", last=True)
        self.assertEqual(new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_unchanged_measurement(self, request):
        """Post an unchanged measurement for a metric."""
        self.database.measurements.find_one.return_value = dict(_id="id", sources=[])
        request.json = dict(metric_uuid="metric_uuid", sources=[])
        self.assertEqual(dict(ok=True), post_measurement(self.database))
        self.database.measurements.update_one.assert_called_once()

    def test_changed_measurement_value(self, request):
        """Post a changed measurement for a metric."""
        self.database.measurements.find_one.return_value = dict(
            _id="id", status="target_met", last=True, sources=[dict(value="0", entities=[])])
        sources = [dict(value="1", parse_error=None, connection_error=None, entities=[])]
        request.json = dict(report_uuid="report_uuid", metric_uuid="metric_uuid", sources=sources)
        new_measurement = dict(
            _id="measurement_id", report_uuid="report_uuid", metric_uuid="metric_uuid", status="near_target_met",
            start="2019-01-01", end="2019-01-01", value="1", last=True, sources=sources)
        self.assertEqual(new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_changed_measurement_entities(self, request):
        """Post a measurement whose value is the same, but with different entities."""
        self.database.measurements.find_one.return_value = dict(
            _id="id", status="target_met", last=True,
            sources=[dict(value="1", entities=[dict(key="a")], entity_user_data=dict(a="attributes"))])
        sources = [dict(value="1", parse_error=None, connection_error=None, entities=[dict(key="b")])]
        request.json = dict(report_uuid="report_uuid", metric_uuid="metric_uuid", sources=sources)
        new_measurement = dict(
            _id="measurement_id", report_uuid="report_uuid", metric_uuid="metric_uuid", status="near_target_met",
            start="2019-01-01", end="2019-01-01", value="1", last=True, sources=sources)
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
        request.json = dict(metric_uuid="metric_uuid", sources=sources)
        self.assertEqual(dict(ok=True), post_measurement(self.database))
        self.database.measurements.update_one.assert_called_once_with(
            filter={'_id': 'id'}, update={'$set': {'end': '2019-01-01', 'last': True}})


class SetEntityAttributeTest(unittest.TestCase):
    """Unit tests for the set entity attribute route."""
    def test_set_attribute(self):
        """Test that setting an attribute inserts a new measurement."""
        database = Mock()
        database.measurements.find_one.return_value = dict(
            _id="id", report_uuid="report_uuid", metric_uuid="metric_uuid", status="red",
            sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")])

        def insert_one(new_measurement):
            new_measurement["_id"] = "id"

        database.measurements.insert_one = insert_one
        database.reports = Mock()
        database.reports.distinct.return_value = ["report_uuid"]
        database.reports.find_one.return_value = dict(
            _id="id",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            type="metric_type", target="0", near_target="10", debt_target="0", accept_debt=False,
                            addition="sum", tags=[])))))
        database.datamodels = Mock()
        database.datamodels.find_one.return_value = dict(_id=123, metrics=dict(metric_type=dict(direction="≦")))
        with patch("bottle.request", Mock(json=dict(attribute="value"))):
            measurement = set_entity_attribute("metric_uuid", "source_uuid", "entity_key", "attribute", database)
        entity = measurement["sources"][0]["entity_user_data"]["entity_key"]
        self.assertEqual(dict(attribute="value"), entity)


class StreamNrMeasurementsTest(unittest.TestCase):
    """Unit tests for the number of measurements stream."""

    def test_stream(self):
        """Test that the stream returns the number of measurements whenever it changes."""
        def sleep(seconds):
            return seconds
        database = Mock()
        database.measurements.count_documents.side_effect = [42, 42, 43]
        with patch("time.sleep", sleep):
            stream = stream_nr_measurements("report_uuid", database)
            self.assertEqual("retry: 2000\nid: 0\nevent: init\ndata: 42\n\n", next(stream))
            self.assertEqual("retry: 2000\nid: 1\nevent: delta\ndata: 43\n\n", next(stream))
