"""Unit tests for the report routes."""

import unittest

from routes.report import (
    delete_metric, delete_report, delete_source, delete_subject, get_changelog, get_metrics, get_reports,
    get_tag_report, post_metric_attribute, post_metric_new, post_new_subject, post_report_attribute, post_report_new,
    post_reports_attribute, post_source_attribute, post_source_new, post_source_parameter, post_subject_attribute
)
from unittest.mock import Mock, patch
from utilities.functions import iso_timestamp


@patch("bottle.request")
class PostReportAttributeTest(unittest.TestCase):
    """Unit tests for the post report attribute route."""
    def test_post_report_name(self, request):
        """Test that the report name can be changed."""
        report = dict(_id="id", report_uuid="report_uuid")
        request.json = dict(name="name")
        database = Mock()
        database.reports.find_one.return_value = report
        database.sessions.find_one.return_value = dict(user="John")
        self.assertEqual(dict(ok=True), post_report_attribute("report_uuid", "name", database))
        database.reports.insert.assert_called_once_with(report)
        self.assertEqual("John changed the report name from '' to 'name'.", report["delta"])


@patch("bottle.request")
class PostSubjectAttributeTest(unittest.TestCase):
    """Unit tests for the post subject report attribute route."""
    def test_post_subject_name(self, request):
        """Test that the subject name can be changed."""
        report = dict(_id="id", report_uuid="report_uuid", subjects=dict(subject_uuid=dict(name="old name")))
        request.json = dict(name="new name")
        database = Mock()
        database.reports.find_one.return_value = report
        database.sessions.find_one.return_value = dict(user="John")
        self.assertEqual(dict(ok=True), post_subject_attribute("report_uuid", "subject_uuid", "name", database))
        database.reports.insert.assert_called_once_with(report)
        self.assertEqual("John changed the name of subject old name from 'old name' to 'new name'.", report["delta"])


@patch("database.reports.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("bottle.request")
class PostMetricAttributeTest(unittest.TestCase):
    """Unit tests for the post metric attribute route."""

    def setUp(self):
        self.report = dict(
            _id="id", report_uuid="report_uuid",
            subjects=dict(
                other_subject=dict(metrics=dict()),
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            name="name", type="old_type", addition="sum", target="0", near_target="10",
                            debt_target=None, accept_debt=False, tags=[], sources=dict(source_uuid=dict()))))))
        self.database = Mock()
        self.database.reports.find_one.return_value = self.report
        self.database.sessions.find_one.return_value = dict(user="John")

    def test_post_metric_name(self, request):
        """Test that the metric name can be changed."""
        request.json = dict(name="ABC")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual("John changed the name of metric name from 'name' to 'ABC'.", self.report["delta"])

    def test_post_metric_type(self, request):
        """Test that the metric type can be changed."""
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            metrics=dict(
                old_type=dict(name="Old type"),
                new_type=dict(addition="sum", target="0", near_target="1", tags=[], sources=["source_type"])))
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            "John changed the type of metric name from 'old_type' to 'new_type'.", self.report["delta"])

    def test_post_metric_target_without_measurements(self, request):
        """Test that changing the metric target doesnt't add a new measurement if none exist."""
        self.database.measurements.find_one.return_value = None
        request.json = dict(target="10")
        self.assertEqual(dict(ok=True), post_metric_attribute("report_uuid", "metric_uuid", "target", self.database))
        self.assertEqual(
            "John changed the target of metric name from '0' to '10'.", self.report["delta"])

    @patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_target_with_measurements(self, request):
        """Test that changing the metric target adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid="metric_uuid", sources=[])

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        request.json = dict(target="10")
        self.assertEqual(
            dict(
                _id="measurement_id", end="2019-01-01", sources=[], start="2019-01-01", status=None, value=None,
                metric_uuid="metric_uuid", last=True),
            post_metric_attribute("report_uuid", "metric_uuid", "target", self.database))
        self.assertEqual(
            "John changed the target of metric name from '0' to '10'.", self.report["delta"])

    @patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_debt_end_date_with_measurements(self, request):
        """Test that changing the metric debt end date adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid="metric_uuid", sources=[])

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        request.json = dict(debt_end_date="2019-06-07")
        self.assertEqual(
            dict(
                _id="measurement_id", end="2019-01-01", sources=[], start="2019-01-01", last=True, status=None,
                metric_uuid="metric_uuid", value=None),
            post_metric_attribute("report_uuid", "metric_uuid", "debt_end_date", self.database))
        self.assertEqual(
            "John changed the debt_end_date of metric name from '' to '2019-06-07'.", self.report["delta"])


@patch("bottle.request")
class PostSourceAttributeTest(unittest.TestCase):
    """Unit tests for the post source attribute route."""

    def setUp(self):
        self.report = dict(
            _id="report_uuid",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(metric_uuid=dict(type="type", sources=dict(source_uuid=dict(type="type")))))))
        self.database = Mock()
        self.database.reports.find_one.return_value = self.report
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="id", sources=dict(type=dict(name="Type"), new_type=dict(parameters=dict())))

    def test_name(self, request):
        """Test that the source name can be changed."""
        request.json = dict(name="name")
        self.assertEqual(dict(ok=True), post_source_attribute("report_uuid", "source_uuid", "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual("Jenny changed the name of source Type from '' to 'name'.", self.report["delta"])

    def test_post_source_type(self, request):
        """Test that the source type can be changed."""
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_source_attribute("report_uuid", "source_uuid", "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual("Jenny changed the type of source Type from 'type' to 'new_type'.", self.report["delta"])


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
                            type="type",
                            sources=dict(source_uuid=dict(name="name", type="type", parameters=dict())))))))
        database = Mock()
        database.sessions.find_one.return_value = dict(user="Jenny")
        database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), post_source_parameter("report_uuid", "source_uuid", "url", database))
        database.reports.insert.assert_called_once_with(report)
        self.assertEqual("Jenny changed the url of source name from '' to 'http://url'.", report["delta"])


class SourceTest(unittest.TestCase):
    """Unit tests for adding and deleting sources."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="",
            metrics=dict(metric_type=dict(name="metric type", direction="≦", default_source="source_type")),
            sources=dict(source_type=dict(parameters=dict())))

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
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), post_source_new("report_uuid", "metric_uuid", self.database))
        self.database.reports.insert.assert_called_once_with(report)
        self.assertEqual("Jenny added a new source to metric metric type.", report["delta"])

    def test_delete_source(self):
        """Test that the source can be deleted."""
        report = dict(
            _id="report_uuid",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            type="type", name="Metric", sources=dict(source_uuid=dict(name="Source")))))))
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), delete_source("report_uuid", "source_uuid", self.database))
        self.database.reports.insert.assert_called_once_with(report)
        self.assertEqual("Jenny deleted the source Source from metric Metric.", report["delta"])


class MetricTest(unittest.TestCase):
    """Unit tests for adding and deleting metrics."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")

    def test_add_metric(self):
        """Test that a metric can be added."""
        report = dict(_id="report_uuid", subjects=dict(subject_uuid=dict(name="Subject", metrics=dict())))
        self.database.reports.find_one.return_value = report
        self.database.datamodels.find_one.return_value = dict(
            _id="",
            metrics=dict(
                metric_type=dict(
                    addition="sum", direction="≦", target="0", near_target="1", tags=[])))
        self.assertEqual(dict(ok=True), post_metric_new("report_uuid", "subject_uuid", self.database))
        self.assertEqual("Jenny added a metric to subject Subject.", report["delta"])

    def test_get_metrics(self):
        """Test that the metrics can be retrieved and deleted reports are skipped."""
        report = dict(
            _id="id", report_uuid="report_uuid",
            subjects=dict(subject_uuid=dict(metrics=dict(metric_uuid=dict(tags=[])))))
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.database.reports.distinct.return_value = ["report_uuid", "deleted_report"]
        self.database.reports.find_one.side_effect = [report, dict(deleted=True)]
        self.database.measurements.find.return_value = [dict(
            _id="id", metric_uuid="metric_uuid", status="red",
            sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")])]
        self.assertEqual(dict(metric_uuid=dict(tags=[])), get_metrics(self.database))

    def test_delete_metric(self):
        """Test that the metric can be deleted."""
        report = dict(
            _id="report_uuid",
            subjects=dict(subject_uuid=dict(name="Subject", metrics=dict(metric_uuid=dict(name="Metric")))))
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), delete_metric("report_uuid", "metric_uuid", self.database))
        self.database.reports.insert.assert_called_once_with(report)
        self.assertEqual("Jenny deleted metric Metric from subject Subject.", report["delta"])


class SubjectTest(unittest.TestCase):
    """Unit tests for adding and deleting subjects."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.report = dict(subjects=dict(subject_uuid=dict(name="ABC")))
        self.database.reports.find_one.return_value = self.report

    def test_add_subject(self):
        """Test that a subject can be added."""
        self.database.datamodels.find_one.return_value = dict(
            _id="", subjects=dict(subject_type=dict(name="Subject", description="")))
        self.assertEqual(dict(ok=True), post_new_subject("report_uuid", self.database))
        self.assertEqual("Jenny created a new subject.", self.report["delta"])

    def test_delete_subject(self):
        """Test that a subject can be deleted."""
        self.assertEqual(dict(ok=True), delete_subject("report_uuid", "subject_uuid", self.database))
        self.assertEqual("Jenny deleted the subject ABC.", self.report["delta"])


class ReportTest(unittest.TestCase):
    """Unit tests for adding, deleting, and getting reports."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")

    def test_add_report(self):
        """Test that a report can be added."""
        self.assertEqual(dict(ok=True), post_report_new(self.database))
        args, kwargs = self.database.reports.insert.call_args
        report = args[0]
        self.assertEqual("Jenny created a new report.", report["delta"])

    def test_get_report(self):
        """Test that a report can be retrieved."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.database.measurements.find.return_value = [
            dict(
                _id="id", metric_uuid="metric_uuid", status="red",
                sources=[dict(source_uuid="source_uuid", parse_error=None, connection_error=None, value="42")])]
        self.database.reports.distinct.return_value = ["report_uuid"]
        report = dict(
            _id="id", report_uuid="report_uuid",
            subjects=dict(
                subject_uuid=dict(
                    metrics=dict(
                        metric_uuid=dict(
                            type="metric_type", target="0", near_target="10", debt_target="0", accept_debt=False,
                            addition="sum", tags=["a"])))))
        self.database.reports.find_one.return_value = report
        report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=1)
        report["summary_by_subject"] = dict(subject_uuid=dict(red=0, green=0, yellow=0, grey=0, white=1))
        report["summary_by_tag"] = {}
        self.assertEqual(dict(_id="id", title="Reports", subtitle="", reports=[report]), get_reports(self.database))

    def test_delete_report(self):
        """Test that the report can be deleted."""
        report = dict(_id="1", report_uuid="report_uuid", title="Foo")
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), delete_report("report_uuid", self.database))
        self.assertEqual("Jenny deleted the report Foo.", report["delta"])

    @patch("bottle.request")
    def test_post_reports_attribute(self, request):
        """Test that a reports (overview) attribute can be changed."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports")
        request.json = dict(title="All the reports")
        self.assertEqual(dict(ok=True), post_reports_attribute("title", self.database))

    @patch("bottle.request")
    def test_get_tag_report(self, request):
        """Test that a tag report can be retrieved."""
        date_time = request.report_date = iso_timestamp()
        self.database.reports.find_one.return_value = None
        self.database.measurements.find.return_value = []
        self.database.reports.distinct.return_value = ["report_uuid"]
        self.database.reports.find_one.return_value = dict(
            _id="id", report_uuid="report_uuid",
            subjects=dict(
                subject_without_metrics=dict(metrics=dict()),
                subject_uuid=dict(
                    metrics=dict(
                        metric_with_tag=dict(tags=["tag"]),
                        metric_without_tag=dict(tags=["other tag"])))))
        self.assertEqual(
            dict(
                summary=dict(red=0, green=0, yellow=0, grey=0, white=1),
                summary_by_tag=dict(tag=dict(red=0, green=0, yellow=0, grey=0, white=1)),
                summary_by_subject=dict(subject_uuid=dict(red=0, green=0, yellow=0, grey=0, white=1)),
                title='Report for tag "tag"', subtitle="Note: tag reports are read-only", report_uuid="tag-tag",
                timestamp=date_time, subjects=dict(
                    subject_uuid=dict(metrics=dict(metric_with_tag=dict(tags=["tag"]))))),
            get_tag_report("tag", self.database))

    def test_get_changelog(self):
        """Test that the changelog is returned."""
        report1 = dict(timestamp="1", delta="delta1")
        report2 = dict(timestamp="2", delta="delta2")
        self.database.reports.find.return_value = [report1, report2]
        self.assertEqual(dict(changelog=[report1, report2]), get_changelog("report_uuid", "10", self.database))
