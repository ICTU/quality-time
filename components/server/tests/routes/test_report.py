"""Unit tests for the report routes."""

import unittest
from unittest.mock import Mock, patch
from typing import cast

from routes.report import (
    delete_metric, delete_report, export_report_as_pdf, get_metrics, get_reports,
    get_tag_report, post_metric_attribute, post_metric_new, post_report_attribute, post_report_new,
    post_reports_attribute, post_report_import
)
from server_utilities.functions import iso_timestamp
from server_utilities.type import MetricId, ReportId, SourceId, SubjectId


METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
REPORT_ID = cast(ReportId, "report_uuid")
SOURCE_ID = cast(SourceId, "source_uuid")
SUBJECT_ID = cast(SubjectId, "subject_uuid")
SUBJECT_ID2 = cast(SubjectId, "subject_uuid2")


@patch("bottle.request")
class PostReportAttributeTest(unittest.TestCase):
    """Unit tests for the post report attribute route."""
    def setUp(self):
        self.database = Mock()
        self.report = dict(_id="id", report_uuid=REPORT_ID, title="Title")
        self.database.reports.find_one.return_value = self.report
        self.database.sessions.find_one.return_value = dict(user="John")
        self.database.datamodels.find_one.return_value = {}

    def test_post_report_title(self, request):
        """Test that the report title can be changed."""
        request.json = dict(title="New title")
        self.assertEqual(dict(ok=True), post_report_attribute(REPORT_ID, "title", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(description="John changed the title of report 'Title' from 'Title' to 'New title'.",
                 report_uuid=REPORT_ID),
            self.report["delta"])

    def test_post_report_layout(self, request):
        """Test that the report layout can be changed."""
        request.json = dict(layout=[dict(x=1, y=2)])
        self.assertEqual(dict(ok=True), post_report_attribute(REPORT_ID, "layout", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(description="John changed the layout of report 'Title'.", report_uuid=REPORT_ID), self.report["delta"])


@patch("database.reports.iso_timestamp", new=Mock(return_value="2019-01-01"))
@patch("bottle.request")
class PostMetricAttributeTest(unittest.TestCase):
    """Unit tests for the post metric attribute route."""

    def setUp(self):
        self.report = dict(
            _id="id", report_uuid=REPORT_ID, title="Report",
            subjects={
                "other_subject": dict(metrics=dict()),
                SUBJECT_ID: dict(
                    name='Subject',
                    metrics={
                        METRIC_ID: dict(
                            name="name", type="old_type", scale="count", addition="sum", direction="<", target="0",
                            near_target="10", debt_target=None, accept_debt=False, tags=[],
                            sources={SOURCE_ID: dict()}),
                        METRIC_ID2: dict(name="name2")})})
        self.database = Mock()
        self.database.reports.find_one.return_value = self.report
        self.database.sessions.find_one.return_value = dict(user="John")
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            metrics=dict(
                old_type=dict(name="Old type", scales=["count"]),
                new_type=dict(
                    scales=["count"], default_scale="count", addition="sum", direction="<", target="0", near_target="1",
                    tags=[], sources=["source_type"])))

    def test_post_metric_name(self, request):
        """Test that the metric name can be changed."""
        request.json = dict(name="ABC")
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID, "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="John changed the name of metric 'name' of subject 'Subject' in report 'Report' "
                             "from 'name' to 'ABC'."),
            self.report["delta"])

    def test_post_metric_type(self, request):
        """Test that the metric type can be changed."""
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID, "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="John changed the type of metric 'name' of subject 'Subject' in report 'Report' "
                             "from 'old_type' to 'new_type'."),
            self.report["delta"])

    def test_post_metric_target_without_measurements(self, request):
        """Test that changing the metric target doesnt't add a new measurement if none exist."""
        self.database.measurements.find_one.return_value = None
        request.json = dict(target="10")
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID, "target", self.database))
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="John changed the target of metric 'name' of subject 'Subject' in report 'Report' "
                             "from '0' to '10'."),
            self.report["delta"])

    @patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_target_with_measurements(self, request):
        """Test that changing the metric target adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        request.json = dict(target="10")
        self.assertEqual(
            dict(
                _id="measurement_id", end="2019-01-01", sources=[], start="2019-01-01",
                count=dict(status=None, value=None), metric_uuid=METRIC_ID, last=True),
            post_metric_attribute(REPORT_ID, METRIC_ID, "target", self.database))
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="John changed the target of metric 'name' of subject 'Subject' in report 'Report' "
                             "from '0' to '10'."),
            self.report["delta"])

    @patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_technical_debt(self, request):
        """Test that accepting techinical debt also sets the technical debt value."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        request.json = dict(accept_debt=True)
        self.assertEqual(
            dict(
                _id="measurement_id", end="2019-01-01", sources=[], start="2019-01-01", last=True,
                metric_uuid=METRIC_ID, count=dict(value=None, status=None)),
            post_metric_attribute(REPORT_ID, METRIC_ID, "accept_debt", self.database))
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="John changed the accept_debt of metric 'name' of subject 'Subject' in report 'Report' "
                             "from '' to 'True'."),
            self.report["delta"])

    @patch("database.measurements.iso_timestamp", new=Mock(return_value="2019-01-01"))
    def test_post_metric_debt_end_date_with_measurements(self, request):
        """Test that changing the metric debt end date adds a new measurement if one or more exist."""
        self.database.measurements.find_one.return_value = dict(_id="id", metric_uuid=METRIC_ID, sources=[])

        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"

        self.database.measurements.insert_one.side_effect = set_measurement_id
        request.json = dict(debt_end_date="2019-06-07")
        self.assertEqual(
            dict(
                _id="measurement_id", end="2019-01-01", sources=[], start="2019-01-01", last=True,
                metric_uuid=METRIC_ID, count=dict(value=None, status=None)),
            post_metric_attribute(REPORT_ID, METRIC_ID, "debt_end_date", self.database))
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="John changed the debt_end_date of metric 'name' of subject 'Subject' in report "
                             "'Report' from '' to '2019-06-07'."),
            self.report["delta"])

    def test_post_unsafe_comment(self, request):
        """Test that comments are sanitized, since they are displayed as inner HTML in the frontend."""
        request.json = dict(comment='Comment with script<script type="text/javascript">alert("Danger")</script>')
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID, "comment", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="John changed the comment of metric 'name' of subject 'Subject' in report 'Report' "
                             "from '' to 'Comment with script'."),
            self.report["delta"])

    def test_post_comment_with_link(self, request):
        """Test that urls in comments are transformed into anchors."""
        request.json = dict(comment='Comment with url https://google.com')
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID, "comment", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="""John changed the comment of metric 'name' of subject 'Subject' in report 'Report' \
from '' to '<p>Comment with url <a href="https://google.com">https://google.com</a></p>'."""),
            self.report["delta"])

    def test_post_position_first(self, request):
        """Test that a metric can be moved to the top of the list."""
        request.json = dict(position="first")
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID2, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID2,
                 description="John changed the position of metric 'name2' of subject 'Subject' in report "
                             "'Report' from '1' to '0'."),
            self.report["delta"])

    def test_post_position_last(self, request):
        """Test that a metric can be moved to the bottom of the list."""
        request.json = dict(position="last")
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="John changed the position of metric 'name' of subject 'Subject' in report "
                             "'Report' from '0' to '1'."),
            self.report["delta"])

    def test_post_position_previous(self, request):
        """Test that a metric can be moved up."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID2, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID2,
                 description="John changed the position of metric 'name2' of subject 'Subject' in report "
                             "'Report' from '1' to '0'."),
            self.report["delta"])

    def test_post_position_next(self, request):
        """Test that a metric can be moved down."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual([METRIC_ID2, METRIC_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="John changed the position of metric 'name' of subject 'Subject' in report "
                             "'Report' from '0' to '1'."),
            self.report["delta"])

    def test_post_position_first_previous(self, request):
        """Test that moving the first metric up does nothing."""
        request.json = dict(position="previous")
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID, "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual([METRIC_ID, METRIC_ID2], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))

    def test_post_position_last_next(self, request):
        """Test that moving the last metric down does nothing."""
        request.json = dict(position="next")
        self.assertEqual(dict(ok=True), post_metric_attribute(REPORT_ID, METRIC_ID2, "position", self.database))
        self.database.reports.insert.assert_not_called()
        self.assertEqual([METRIC_ID, METRIC_ID2], list(self.report["subjects"][SUBJECT_ID]["metrics"].keys()))


class MetricTest(unittest.TestCase):
    """Unit tests for adding and deleting metrics."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="",
            metrics=dict(
                metric_type=dict(
                    default_scale="count", addition="sum", direction="<", target="0", near_target="1", tags=[])))

    def test_add_metric(self):
        """Test that a metric can be added."""
        report = dict(_id=REPORT_ID, title="Report", subjects={SUBJECT_ID: dict(name="Subject", metrics=dict())})
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), post_metric_new(REPORT_ID, SUBJECT_ID, self.database))
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID,
                 description="Jenny added a new metric to subject 'Subject' in report 'Report'."),
            report["delta"])

    def test_get_metrics(self):
        """Test that the metrics can be retrieved and deleted reports are skipped."""
        report = dict(
            _id="id", report_uuid=REPORT_ID,
            subjects={SUBJECT_ID: dict(metrics={METRIC_ID: dict(type="metric_type", tags=[])})})
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.database.reports.distinct.return_value = [REPORT_ID, "deleted_report"]
        self.database.reports.find_one.side_effect = [report, dict(deleted=True)]
        self.database.measurements.find.return_value = [dict(
            _id="id", metric_uuid=METRIC_ID, status="red",
            sources=[dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42")])]
        self.assertEqual({METRIC_ID: dict(type="metric_type", tags=[])}, get_metrics(self.database))

    def test_delete_metric(self):
        """Test that the metric can be deleted."""
        report = dict(
            _id=REPORT_ID, title="Report",
            subjects={SUBJECT_ID: dict(name="Subject", metrics={METRIC_ID: dict(name="Metric")})})
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), delete_metric(REPORT_ID, METRIC_ID, self.database))
        self.database.reports.insert.assert_called_once_with(report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID,
                 description=f"Jenny deleted metric 'Metric' from subject 'Subject' in report 'Report'."),
            report["delta"])


class ReportTest(unittest.TestCase):
    """Unit tests for adding, deleting, and getting reports."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")

    def test_add_report(self):
        """Test that a report can be added."""
        self.assertEqual(dict(ok=True), post_report_new(self.database))
        self.database.reports.insert.assert_called_once()
        inserted = self.database.reports.insert.call_args_list[0][0][0]
        self.assertEqual("New report", inserted["title"])
        self.assertEqual("Jenny created a new report.", inserted["delta"]["description"])

    def test_get_report(self):
        """Test that a report can be retrieved."""
        self.database.datamodels.find_one.return_value = dict(
            _id="id", metrics=dict(metric_type=dict(default_scale="count")))
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports", subtitle="")
        self.database.measurements.find.return_value = [
            dict(
                _id="id", metric_uuid=METRIC_ID, status="red",
                sources=[dict(source_uuid=SOURCE_ID, parse_error=None, connection_error=None, value="42")])]
        self.database.reports.distinct.return_value = [REPORT_ID]
        report = dict(
            _id="id", report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID: dict(
                    metrics={
                        METRIC_ID: dict(
                            type="metric_type", addition="sum", target="0", near_target="10", debt_target="0",
                            accept_debt=False, tags=["a"])})})
        self.database.reports.find_one.return_value = report
        report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=1)
        report["summary_by_subject"] = {SUBJECT_ID: dict(red=0, green=0, yellow=0, grey=0, white=1)}
        report["summary_by_tag"] = {}
        self.assertEqual(dict(_id="id", title="Reports", subtitle="", reports=[report]), get_reports(self.database))

    @patch("requests.get")
    def test_get_pdf_report(self, requests_get):
        """Test that a PDF version of the report can be retrieved."""
        response = Mock()
        response.content = b"PDF"
        requests_get.return_value = response
        self.assertEqual(b"PDF", export_report_as_pdf("report_uuid"))

    def test_delete_report(self):
        """Test that the report can be deleted."""
        self.database.datamodels.find_one.return_value = dict(_id="id")
        report = dict(_id="1", report_uuid=REPORT_ID, title="Report")
        self.database.reports.find_one.return_value = report
        self.assertEqual(dict(ok=True), delete_report(REPORT_ID, self.database))
        inserted = self.database.reports.insert.call_args_list[0][0][0]
        self.assertEqual("Jenny deleted the report 'Report'.", inserted["delta"]["description"])

    @patch("bottle.request")
    def test_post_reports_attribute_title(self, request):
        """Test that a reports (overview) attribute can be changed."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports")
        request.json = dict(title="All the reports")
        self.assertEqual(dict(ok=True), post_reports_attribute("title", self.database))
        inserted = self.database.reports_overviews.insert.call_args_list[0][0][0]
        self.assertEqual(
            "Jenny changed the title of the reports overview from 'Reports' to 'All the reports'.",
            inserted["delta"]["description"])

    @patch("bottle.request")
    def test_post_reports_attribute_layout(self, request):
        """Test that a reports (overview) layout can be changed."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", title="Reports")
        request.json = dict(layout=[dict(x=1, y=2)])
        self.assertEqual(dict(ok=True), post_reports_attribute("layout", self.database))
        inserted = self.database.reports_overviews.insert.call_args_list[0][0][0]
        self.assertEqual("Jenny changed the layout of the reports overview.", inserted["delta"]["description"])

    @patch("bottle.request")
    def test_post_report_import(self, request):
        """Test that a report is imported correctly."""
        request.json = dict(_id="id", title="Title", report_uuid="report_uuid", subjects={})
        post_report_import(self.database)
        inserted = self.database.reports.insert.call_args_list[0][0][0]
        self.assertEqual("Title", inserted["title"])
        self.assertEqual("report_uuid", inserted["report_uuid"])

    @patch("bottle.request")
    def test_get_tag_report(self, request):
        """Test that a tag report can be retrieved."""
        date_time = request.report_date = iso_timestamp()
        self.database.datamodels.find_one.return_value = dict(
            _id="id", metrics=dict(metric_type=dict(default_scale="count")))
        self.database.reports.find_one.return_value = None
        self.database.measurements.find.return_value = []
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.reports.find_one.return_value = dict(
            _id="id", report_uuid=REPORT_ID, title="Report",
            subjects={
                "subject_without_metrics": dict(metrics=dict()),
                SUBJECT_ID: dict(
                    name="Subject",
                    metrics=dict(
                        metric_with_tag=dict(type="metric_type", tags=["tag"]),
                        metric_without_tag=dict(type="metric_type", tags=["other tag"])))})
        self.assertDictEqual(
            dict(
                summary=dict(red=0, green=0, yellow=0, grey=0, white=1),
                summary_by_tag=dict(tag=dict(red=0, green=0, yellow=0, grey=0, white=1)),
                summary_by_subject={SUBJECT_ID: dict(red=0, green=0, yellow=0, grey=0, white=1)},
                title='Report for tag "tag"', subtitle="Note: tag reports are read-only", report_uuid="tag-tag",
                timestamp=date_time, subjects={
                    SUBJECT_ID: dict(
                        name="Report / Subject",
                        metrics=dict(metric_with_tag=dict(type="metric_type", tags=["tag"])))}),
            get_tag_report("tag", self.database))
