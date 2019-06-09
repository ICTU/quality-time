"""Unit tests for the report routes."""

import unittest
from unittest.mock import Mock, patch

from src.routes.report import delete_metric, delete_report, delete_source, delete_subject, get_metrics, get_reports, \
    post_metric_attribute, post_metric_new, post_new_subject, post_report_attribute, post_report_new, \
    post_source_attribute, post_source_new, post_source_parameter, post_subject_attribute


@patch("bottle.request")
class PostReportAttributeTest(unittest.TestCase):
    """Unit tests for the post report attribute route."""
    def test_post_report_name(self, request):
        """Test that the report name can be changed."""
        report = dict(_id="report_uuid")
        request.json = dict(name="name")
        database = Mock()
        database.reports.find_one = Mock(return_value=report)
        self.assertEqual(dict(ok=True), post_report_attribute(
            "report_uuid", "name", database))
        database.reports.insert.assert_called_once_with(report)


@patch("bottle.request")
class PostSubjecrAttributeTest(unittest.TestCase):
    """Unit tests for the post subjecr report attribute route."""
    def test_post_subject_name(self, request):
        """Test that the subject name can be changed."""
        report = dict(_id="report_uuid", subjects=dict(subject_uuid=dict()))
        request.json = dict(name="name")
        database = Mock()
        database.reports.find_one = Mock(return_value=report)
        self.assertEqual(dict(ok=True), post_subject_attribute(
            "report_uuid", "subject_uuid", "name", database))
        database.reports.insert.assert_called_once_with(report)


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
        self.assertEqual(dict(ok=True), post_metric_attribute(
            "report_uuid", "metric_uuid", "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)

    def test_post_metric_type(self, request):
        """Test that the metric type can be changed."""
        self.database.datamodels.find_one = Mock(return_value=dict(
            _id="id",
            metrics=dict(new_type=dict(addition="sum", target="0", near_target="1", tags=[], sources=["source_type"]))))
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_metric_attribute(
            "report_uuid", "metric_uuid", "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)

    def test_post_metric_target_without_measurements(self, request):
        """Test that changing the metric target doesnt't add a new measurement if none exist."""
        self.database.measurements.find_one = Mock(return_value=None)
        request.json = dict(target="10")
        self.assertEqual(dict(ok=True), post_metric_attribute(
            "report_uuid", "metric_uuid", "target", self.database))

    @patch("src.database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_target_with_measurements(self, request):
        """Test that changing the metric target adds a new measurement if one or more exist."""
        self.database.measurements.find_one = Mock(
            return_value=dict(_id="id", sources=[]))

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"
        self.database.measurements.insert_one = Mock(
            side_effect=set_measurement_id)
        request.json = dict(target="10")
        self.assertEqual(
            dict(_id="measurement_id", end="2019-01-01", sources=[],
                 start="2019-01-01", status=None, value=None),
            post_metric_attribute("report_uuid", "metric_uuid", "target", self.database))


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
        self.assertEqual(dict(ok=True), post_source_attribute(
            "report_uuid", "source_uuid", "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)

    def test_post_source_type(self, request):
        """Test that the source type can be changed."""
        self.database.datamodels.find_one = Mock(return_value=dict(
            _id="id", sources=dict(new_type=dict(parameters=dict()))))
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_source_attribute(
            "report_uuid", "source_uuid", "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)


@patch("bottle.request")
class PostSourceParameterTest(unittest.TestCase):
    """Unit tests for the post source parameter route."""

    def test_url(self, request):
        """Test that the source url can be changed."""
        request.json = dict(url="http://url")
        report = dict(
            _id="report_uuid",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            type="type", sources=dict(source_uuid=dict(type="type", parameters=dict())))))))
        database = Mock()
        database.reports.find_one = Mock(return_value=report)
        self.assertEqual(dict(ok=True), post_source_parameter(
            "report_uuid", "source_uuid", "url", database))
        database.reports.insert.assert_called_once_with(report)


class SourceTest(unittest.TestCase):
    """Unit tests for adding and deleting sources."""

    def test_add_source(self):
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
            metrics=dict(metric_type=dict(
                direction="<=", default_source="source_type")),
            sources=dict(source_type=dict(parameters=dict()))))
        self.assertEqual(dict(ok=True), post_source_new(
            "report_uuid", "metric_uuid", database))
        database.reports.insert.assert_called_once_with(report)

    def test_delete_source(self):
        """Test that the source can be deleted."""
        report = dict(
            _id="report_uuid",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            type="type", sources=dict(source_uuid=dict()))))))
        database = Mock()
        database.reports.find_one = Mock(return_value=report)
        self.assertEqual(dict(ok=True), delete_source(
            "report_uuid", "source_uuid", database))
        database.reports.insert.assert_called_once_with(report)


class MetricTest(unittest.TestCase):
    """Unit tests for adding and deleting metrics."""

    def test_add_metric(self):
        """Test that a metric can be added."""
        report = dict(_id="report_uuid", subjects=dict(subject_uuid=dict(metrics=dict())))
        database = Mock()
        database.reports.find_one = Mock(return_value=report)
        database.datamodels.find_one = Mock(
            return_value=dict(
                _id="",
                metrics=dict(
                    metric_type=dict(
                        addition="sum", direction="<=", target="0", near_target="1", tags=[]))))
        self.assertEqual(dict(ok=True), post_metric_new("report_uuid", "subject_uuid", database))

    def test_get_metrics(self):
        """Test that the metrics can be retrieved and deleted reports are skipped."""
        report = dict(_id="report_uuid", subjects=dict(subject_uuid=dict(metrics=dict(metric_uuid=dict(tags=[])))))
        database = Mock()
        database.reports.distinct = Mock(return_value=["report_uuid", "deleted_report"])
        database.reports.find_one = Mock(side_effect=[report, dict(deleted=True)])
        database.measurements.find_one = Mock(
            return_value=dict(
                _id="id", metric_uuid="metric_uuid", status="red",
                sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")]))
        self.assertEqual(dict(metric_uuid=dict(tags=[])), get_metrics(database))

    def test_delete_metric(self):
        """Test that the metric can be deleted."""
        report = dict(_id="report_uuid", subjects=dict(subject_uuid=dict(metrics=dict(metric_uuid=dict()))))
        database = Mock()
        database.reports.find_one = Mock(return_value=report)
        self.assertEqual(dict(ok=True), delete_metric("report_uuid", "metric_uuid", database))
        database.reports.insert.assert_called_once_with(report)


class SubjectTest(unittest.TestCase):
    """Unit tests for adding and deleting subjects."""

    def test_add_subject(self):
        """Test that a subject can be added."""
        report = dict(_id="report_uuid", subjects=dict())
        database = Mock()
        database.reports.find_one = Mock(return_value=report)
        database.datamodels.find_one = Mock(return_value=dict(
            _id="", subjects=dict(subject_type=dict(name="Subject", description=""))))
        self.assertEqual(dict(ok=True), post_new_subject("report_uuid", database))

    def test_delete_subject(self):
        """Test that a subject can be deleted."""
        database = Mock()
        report = dict(subjects=dict(subject_uuid=dict()))
        database.reports.find_one = Mock(return_value=report)
        self.assertEqual(dict(ok=True), delete_subject("report_uuid", "subject_uuid", database))


class ReportTest(unittest.TestCase):
    """Unit tests for adding, deleting, and getting reports."""

    def test_add_report(self):
        """Test that a report can be added."""
        database = Mock()
        self.assertEqual(dict(ok=True), post_report_new(database))

    def test_get_report(self):
        """Test that a report can be retrieved."""
        database = Mock()
        database.measurements.find_one = Mock(
            return_value=dict(
                _id="id", metric_uuid="metric_uuid", status="red",
                sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")]))
        database.reports.distinct = Mock(return_value=["report_uuid"])
        report = dict(
            _id="id",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            type="metric_type", target="0", near_target="10", debt_target="0", accept_debt=False,
                            addition="sum", tags=["a"])))))
        database.reports.find_one = Mock(return_value=report)
        report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=1)
        report["summary_by_subject"] = dict(subject_uuid=dict(red=0, green=0, yellow=0, grey=0, white=1))
        report["summary_by_tag"] = {}
        self.assertEqual(dict(reports=[report]), get_reports(database))

    def test_delete_report(self):
        """Test that the report can be deleted."""
        report = dict(_id="report_uuid")
        database = Mock()
        database.reports.find_one = Mock(return_value=report)
        self.assertEqual(dict(ok=True), delete_report("report_uuid", database))
