"""Unit tests for the report class."""

from shared.model.metric import Metric
from shared.model.report import Report
from shared.model.source import Source
from shared.model.subject import Subject

from ...fixtures import METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID

from ..base import DataModelTestCase


class ReportTest(DataModelTestCase):
    """Report unit tests."""

    def setUp(self) -> None:
        """Override to create a database fixture."""
        self.source_data = {}
        self.metric_data = dict(type="violations", sources={SOURCE_ID: self.source_data}, tags=["tag"])
        self.subject_data = dict(metrics={METRIC_ID: self.metric_data})
        report_data = dict(
            report_uuid=REPORT_ID,
            title="Report",
            subjects={SUBJECT_ID: self.subject_data},
        )
        self.report = Report(self.DATA_MODEL, report_data)

    def test_uuid(self):
        """Test that the report uuid can be retrieved."""
        self.assertEqual("report_uuid", self.report.uuid)

    def test_id(self):
        """Test that a Mongo ID is stringified."""
        report = Report(self.DATA_MODEL, dict(_id=123))
        self.assertEqual("123", report["_id"])

    def test_name(self):
        """Test that the report name equals the report title."""
        self.assertEqual("Report", self.report.name)

    def test_equality(self):
        """Test that reports are equal if their ids are."""
        self.assertEqual(Report(self.DATA_MODEL, dict(report_uuid=REPORT_ID)), self.report)

    def test_subjects_dict(self):
        """Test that the subjects can be retrieved."""
        self.assertEqual(
            {SUBJECT_ID: Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report)},
            self.report.subjects_dict,
        )

    def test_subject_dict_with_instantiated_subjects(self):
        """Test that instantiated subjects can be retrieved."""
        subject = Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report)
        report = Report(self.DATA_MODEL, dict(subjects={SUBJECT_ID: subject}))
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
            METRIC_ID: dict(
                latest_measurement=None,
                recent_measurements=[],
                scale="count",
                sources={SOURCE_ID: {}},
                status=None,
                status_start=None,
                type="violations",
                tags=["tag"],
            )
        }
        summary = dict(blue=0, green=0, grey=0, red=0, white=1, yellow=0)
        report_summary = dict(
            title="Report",
            report_uuid=REPORT_ID,
            subjects={SUBJECT_ID: dict(metrics=metrics)},
            summary=summary,
        )
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
