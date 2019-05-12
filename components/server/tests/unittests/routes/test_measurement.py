"""Unit tests for the measurement routes."""

import unittest
from unittest.mock import Mock, patch

from src.routes.measurement import post_measurement


@patch("src.database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("bottle.request")
class PostMeasurementTests(unittest.TestCase):
    """Unit tests for the post measurement route."""

    def setUp(self):
        self.database = Mock()
        report = dict(
            _id="report_uuid",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            name="name", type="metric_type", addition="sum", target="0", near_target="10",
                            debt_target=None, accept_debt=False, tags=[], sources=dict(source_uuid=dict()))))))
        self.database.reports.find_one = Mock(return_value=report)
        self.database.reports.distinct = Mock(return_value=["report_uuid"])
        self.database.datamodels.find_one = Mock(
            return_value=dict(_id="", metrics=dict(metric_type=dict(direction="<="))))
        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"
        self.database.measurements.insert_one = Mock(side_effect=set_measurement_id)
        self.database.measurements.update_one = Mock()

    def test_first_measurement(self, request):
        """Post the first measurement for a metric."""
        self.database.measurements.find_one = Mock(return_value=None)
        request.json = dict(metric_uuid="metric_uuid", sources=[])
        new_measurement = dict(_id="measurement_id", metric_uuid="metric_uuid", sources=[], value=None, status=None,
                               start="2019-01-01", end="2019-01-01")
        self.assertEqual(new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_unchanged_measurement(self, request):
        """Post an unchanged measurement for a metric."""
        self.database.measurements.find_one = Mock(return_value=dict(_id="id", sources=[]))
        request.json = dict(metric_uuid="metric_uuid", sources=[])
        self.assertEqual(dict(ok=True), post_measurement(self.database))
        self.database.measurements.update_one.assert_called_once()

    def test_changed_measurement_value(self, request):
        """Post a changed measurement for a metric."""
        self.database.measurements.find_one = Mock(return_value=dict(
            _id="id", status="target_met", sources=[dict(value="0", units=[])]))
        sources = [dict(value="1", parse_error=None, connection_error=None, units=[])]
        request.json = dict(metric_uuid="metric_uuid", sources=sources)
        new_measurement = dict(_id="measurement_id", metric_uuid="metric_uuid", status="near_target_met",
                               start="2019-01-01", end="2019-01-01", value="1", sources=sources)
        self.assertEqual(new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_changed_measurement_units(self, request):
        """Post a measurement whose value is the same, but with different units."""
        self.database.measurements.find_one = Mock(return_value=dict(
            _id="id", status="target_met", sources=[dict(value="1", units=[dict(key="a")])]))
        sources = [dict(value="1", parse_error=None, connection_error=None, units=[dict(key="b")])]
        request.json = dict(metric_uuid="metric_uuid", sources=sources)
        new_measurement = dict(_id="measurement_id", metric_uuid="metric_uuid", status="near_target_met",
                               start="2019-01-01", end="2019-01-01", value="1", sources=sources)
        self.assertEqual(new_measurement, post_measurement(self.database))
        self.database.measurements.insert_one.assert_called_once()

    def test_ignored_measurement_units(self, request):
        """Post a measurement where the old one has ignored units."""
        self.database.measurements.find_one = Mock(return_value=dict(
            _id="id", status="target_met",
            sources=[
                dict(value="1", parse_error=None, connection_error=None,
                     unit_attributes=dict(status=dict(unit1="false_positive"), rationale=dict(unit1="Rationale")),
                     units=[dict(key="unit1")])]))
        sources = [dict(value="1", parse_error=None, connection_error=None, units=[dict(key="unit1")])]
        request.json = dict(metric_uuid="metric_uuid", sources=sources)
        self.assertEqual(dict(ok=True), post_measurement(self.database))
        self.database.measurements.update_one.assert_called_once_with(
            filter={'_id': 'id'}, update={'$set': {'end': '2019-01-01'}})
