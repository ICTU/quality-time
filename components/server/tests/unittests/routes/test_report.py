"""Unit tests for the report routes."""

import unittest
from unittest.mock import Mock, patch

from src.routes.report import post_metric_attribute, post_source_attribute, post_source_new


@patch("src.database.reports.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("bottle.request")
class PostMetricAttributeTest(unittest.TestCase):
    """Unit tests for the post metric attribute route."""

    def setUp(self):
        self.report = dict(
            _id="report_uuid",
            subjects=dict(
                other_subject=dict(metrics=dict()),
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            name="name", type="old_type", addition="sum", target="0", near_target="10",
                            debt_target=None, accept_debt=False, tags=[], sources=dict(source_uuid=dict()))))))
        self.database = Mock()
        self.database.reports.find_one = Mock(return_value=self.report)

    def test_post_metric_name(self, request):
        """Test that the metric name can be changed."""
        request.json = dict(name="name")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)

    def test_post_metric_type(self, request):
        """Test that the metric type can be changed."""
        self.database.datamodels.find_one = Mock(return_value=dict(
            _id="id",
            metrics=dict(new_type=dict(addition="sum", target="0", near_target="1", tags=[], sources=["source_type"]))))
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)

    def test_post_metric_target_without_measurements(self, request):
        """Test that changing the metric target doesnt't add a new measurement if none exist."""
        self.database.measurements.find_one = Mock(return_value=None)
        request.json = dict(target="10")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "target", self.database))

    @patch("src.database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_target_with_measurements(self, request):
        """Test that changing the metric target adds a new measurement if one or more exist."""
        self.database.measurements.find_one = Mock(return_value=dict(_id="id", sources=[]))
        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"
        self.database.measurements.insert_one = Mock(side_effect=set_measurement_id)
        request.json = dict(target="10")
        self.assertEqual(
            dict(_id="measurement_id", end="2019-01-01", sources=[], start="2019-01-01", status=None, value=None),
            post_metric_attribute("report_uuid", "metric_uuid", "target", self.database))


class PostSourceNewTest(unittest.TestCase):
    """Unit tests for the post new source route."""

    def test_new_source(self):
        """Test that a new source is added."""
        report = dict(
            _id="report_uuid",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            name=None, type="metric_type", addition="sum", target="0", near_target="10",
                            debt_target=None, accept_debt=False, tags=[], sources=dict())))))
        database = Mock()
        database.reports.find_one = Mock(return_value=report)
        database.datamodels.find_one = Mock(return_value=dict(
            _id="",
            metrics=dict(metric_type=dict(direction="<=", sources=["source_type"])),
            sources=dict(source_type=dict(parameters=dict()))))
        self.assertEqual(dict(ok=True), post_source_new("report_uuid", "metric_uuid", database))
        database.reports.insert.assert_called_once_with(report)


@patch("bottle.request")
class PostSourceAttributeTest(unittest.TestCase):
    """Unit tests for the post source attribute route."""

    def setUp(self):
        self.report = dict(
            _id="report_uuid",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(type="type", sources=dict(source_uuid=dict(type="type")))))))
        self.database = Mock()
        self.database.reports.find_one = Mock(return_value=self.report)

    def test_name(self, request):
        """Test that the source name can be changed."""
        request.json = dict(name="name")
        self.assertEqual(dict(ok=True), post_source_attribute("report_uuid", "source_uuid", "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)

    def test_post_source_type(self, request):
        """Test that the source type can be changed."""
        self.database.datamodels.find_one = Mock(return_value=dict(
            _id="id", sources=dict(new_type=dict(parameters=dict()))))
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_source_attribute("report_uuid", "source_uuid", "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
