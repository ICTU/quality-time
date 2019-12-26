"""Unit tests for the report routes."""

import unittest
from unittest.mock import Mock, patch
from typing import cast

from routes.report import (
    delete_report, export_report_as_pdf, get_reports, get_tag_report, post_report_attribute, post_report_new,
    post_reports_attribute, post_report_import
)
from server_utilities.functions import iso_timestamp
from server_utilities.type import ReportId

from .fixtures import METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID


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
        self.assertEqual(b"PDF", export_report_as_pdf(cast(ReportId, "report_uuid")))

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
