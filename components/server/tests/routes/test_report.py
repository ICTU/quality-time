"""Unit tests for the report routes."""

import unittest
from unittest.mock import Mock, patch
from typing import cast

from routes.report import (
    delete_report, export_report_as_pdf, get_tag_report, post_report_attribute, post_report_copy, post_report_new,
    post_report_import)
from server_utilities.functions import iso_timestamp
from server_utilities.type import ReportId

from .fixtures import REPORT_ID, SUBJECT_ID, create_report


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
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            subjects=dict(subject_type=dict(name="Subject type")),
            metrics=dict(metric_type=dict(name="Metric type")),
            sources=dict(source_type=dict(name="Source type")))

    def test_add_report(self):
        """Test that a report can be added."""
        self.assertEqual(dict(ok=True), post_report_new(self.database))
        self.database.reports.insert.assert_called_once()
        inserted = self.database.reports.insert.call_args_list[0][0][0]
        self.assertEqual("New report", inserted["title"])
        self.assertEqual("Jenny created a new report.", inserted["delta"]["description"])

    def test_copy_report(self):
        """Test that a report can be copied."""
        self.database.reports.find_one.return_value = report = create_report()
        self.assertEqual(dict(ok=True), post_report_copy(REPORT_ID, self.database))
        self.database.reports.insert.assert_called_once()
        inserted_report = self.database.reports.insert.call_args[0][0]
        inserted_report_uuid = inserted_report["report_uuid"]
        self.assertNotEqual(report["report_uuid"], inserted_report_uuid)
        self.assertEqual(
            dict(report_uuid=inserted_report_uuid, description="Jenny copied the report 'Report'."),
            inserted_report["delta"])

    @patch("requests.get")
    def test_get_pdf_report(self, requests_get):
        """Test that a PDF version of the report can be retrieved."""
        response = Mock()
        response.content = b"PDF"
        requests_get.return_value = response
        self.assertEqual(b"PDF", export_report_as_pdf(cast(ReportId, "report_uuid")))

    def test_delete_report(self):
        """Test that the report can be deleted."""
        self.database.reports.find_one.return_value = create_report()
        self.assertEqual(dict(ok=True), delete_report(REPORT_ID, self.database))
        inserted = self.database.reports.insert.call_args_list[0][0][0]
        self.assertEqual("Jenny deleted the report 'Report'.", inserted["delta"]["description"])

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
        self.maxDiff = None  # pylint: disable=invalid-name
        request.query = dict(report_date=(date_time := iso_timestamp()))
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
