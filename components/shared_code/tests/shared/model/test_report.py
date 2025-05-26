"""Unit tests for the report class."""

import unittest
from typing import TYPE_CHECKING

import mongomock

from shared.database.reports import get_reports
from shared.model.metric import Metric
from shared.model.report import Report, get_metrics_from_reports
from shared.model.source import Source
from shared.model.subject import Subject

from tests.fixtures import METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID, create_report
from tests.shared.base import DataModelTestCase

if TYPE_CHECKING:
    from pymongo.database import Database


class ReportTest(DataModelTestCase):
    """Report unit tests."""

    def setUp(self) -> None:
        """Override to create a database fixture."""
        self.source_data: dict = {}
        self.metric_data = {"type": "violations", "sources": {SOURCE_ID: self.source_data}, "tags": ["tag"]}
        self.subject_data = {"metrics": {METRIC_ID: self.metric_data}}
        report_data = {
            "report_uuid": REPORT_ID,
            "title": "Report",
            "subjects": {SUBJECT_ID: self.subject_data},
        }
        self.report = Report(self.DATA_MODEL, report_data)

    def test_uuid(self):
        """Test that the report uuid can be retrieved."""
        self.assertEqual("report_uuid", self.report.uuid)

    def test_id(self):
        """Test that a Mongo ID is stringified."""
        report = Report(self.DATA_MODEL, {"_id": 123})
        self.assertEqual("123", report["_id"])

    def test_name(self):
        """Test that the report name equals the report title."""
        self.assertEqual("Report", self.report.name)

    def test_equality(self):
        """Test that reports are equal if their ids are."""
        self.assertEqual(Report(self.DATA_MODEL, {"report_uuid": REPORT_ID}), self.report)

    def test_subjects_dict(self):
        """Test that the subjects can be retrieved."""
        self.assertEqual(
            {SUBJECT_ID: Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report)},
            self.report.subjects_dict,
        )

    def test_subject_dict_with_instantiated_subjects(self):
        """Test that instantiated subjects can be retrieved."""
        subject = Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report)
        report = Report(self.DATA_MODEL, {"subjects": {SUBJECT_ID: subject}})
        self.assertEqual(
            {SUBJECT_ID: Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report)},
            report.subjects_dict,
        )

    def test_metric_uuids(self):
        """Test that the metric uuids can be retrieved."""
        self.assertEqual({METRIC_ID}, self.report.metric_uuids)

    def test_source_uuids(self):
        """Test that the source uuids can be retrieved."""
        self.assertEqual({SOURCE_ID}, self.report.source_uuids)

    def test_summarize(self):
        """Test that the report can be sumamrized."""
        metrics = {
            METRIC_ID: {
                "latest_measurement": None,
                "recent_measurements": [],
                "scale": "count",
                "sources": {SOURCE_ID: {}},
                "status": None,
                "status_start": None,
                "type": "violations",
                "tags": ["tag"],
            },
        }
        summary = {"blue": 0, "green": 0, "grey": 0, "red": 0, "white": 1, "yellow": 0}
        report_summary = {
            "title": "Report",
            "report_uuid": REPORT_ID,
            "subjects": {SUBJECT_ID: {"metrics": metrics}},
            "summary": summary,
        }
        self.assertEqual(report_summary, self.report.summarize({}))

    def test_find_metric(self):
        """Test finding a metric in a report."""
        metric = Metric(self.DATA_MODEL, self.metric_data, METRIC_ID)
        subject = Subject(self.DATA_MODEL, self.subject_data, SUBJECT_ID, self.report)
        self.assertEqual(
            (metric, subject),
            self.report.instance_and_parents_for_uuid(metric_uuid=METRIC_ID),
        )

    def test_find_source(self):
        """Test finding a source in a report."""
        metric = Metric(self.DATA_MODEL, self.metric_data, METRIC_ID)
        source = Source(SOURCE_ID, metric, self.source_data)
        subject = Subject(self.DATA_MODEL, self.subject_data, SUBJECT_ID, self.report)
        self.assertEqual(
            (source, metric, subject),
            self.report.instance_and_parents_for_uuid(source_uuid=SOURCE_ID),
        )

    def test_find_without_source_and_metric_uuid(self):
        """Test that passing neither a source or a metric uuid throws an exception."""
        self.assertRaises(RuntimeError, self.report.instance_and_parents_for_uuid)

    def test_delete_tag(self):
        """Test that a tag can be deleted from all metrics in the report."""
        self.assertEqual([REPORT_ID, SUBJECT_ID, METRIC_ID], self.report.delete_tag("tag"))
        for metric in self.report.metrics:
            self.assertNotIn("tag", metric["tags"])

    def test_delete_tag_not_found(self):
        """Test that deleting a tag that is not in the report does not change the tags."""
        tags = {metric.uuid: metric.get("tags", []) for metric in self.report.metrics}
        self.assertEqual([], self.report.delete_tag("non-existing tag"))
        self.assertEqual(tags, {metric.uuid: metric.get("tags", []) for metric in self.report.metrics})

    def test_rename_tag(self):
        """Test that a tag can be renamed for all metrics in the report."""
        tags = {metric.uuid: metric.get("tags", []) for metric in self.report.metrics}
        expected_tags = {uuid: ["new tag" if tag == "tag" else tag for tag in tags] for (uuid, tags) in tags.items()}
        self.assertEqual([REPORT_ID, SUBJECT_ID, METRIC_ID], self.report.rename_tag("tag", "new tag"))
        self.assertEqual(expected_tags, {metric.uuid: metric.get("tags", []) for metric in self.report.metrics})

    def test_rename_tag_not_found(self):
        """Test that renaming a tag that is not in the report does not change the tags."""
        expected_tags = {metric.uuid: metric.get("tags", []) for metric in self.report.metrics}
        self.assertEqual([], self.report.rename_tag("non-existing tag", "new tag"))
        self.assertEqual(expected_tags, {metric.uuid: metric.get("tags", []) for metric in self.report.metrics})


class TestMetrics(unittest.TestCase):
    """Test set for metrics."""

    def setUp(self) -> None:
        """Define info that is used in multiple tests."""
        self.database: Database = mongomock.MongoClient()["quality_time_db"]

    def test_get_metrics_from_reports(self):
        """Test that the metrics are returned."""
        report = create_report(metric_id=METRIC_ID)
        self.database["reports"].insert_one(report)
        reports = get_reports(self.database)
        metrics = get_metrics_from_reports(reports)
        self.assertEqual(metrics[METRIC_ID]["name"], report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["name"])
        self.assertEqual(metrics[METRIC_ID]["issue_tracker"], report["issue_tracker"])
