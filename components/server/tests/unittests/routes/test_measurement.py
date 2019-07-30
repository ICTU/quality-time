"""Unit tests for the measurement routes."""

import unittest
from unittest.mock import Mock, patch

from src.routes.measurement import get_measurements, set_entity_attribute, stream_nr_measurements


class GetMeasurementsTest(unittest.TestCase):
    """Unit tests for the get measurements route."""

    def test_get_measurements(self):
        """Tests that the measurements for the requested metric are returned."""
        database = Mock()
        database.measurements.find.return_value = [dict(_id="id")]
        self.assertEqual(dict(measurements=[dict(_id="id")]), get_measurements("metric_uuid", database))


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
