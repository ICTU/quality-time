"""Test the subject model."""

from shared.model.metric import Metric
from shared.model.report import Report
from shared.model.subject import Subject

from ...fixtures import METRIC_ID, SUBJECT_ID

from ..base import DataModelTestCase


class SubjectTest(DataModelTestCase):
    """Unit tests for the subject model."""

    def setUp(self) -> None:
        """Override to create a database fixture."""
        self.report = Report(self.DATA_MODEL, dict(title="Report"))

    def test_equality(self):
        """Test that two subjects with the same uuid are equal."""
        self.assertEqual(
            Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report),
            Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report),
        )

    def test_type(self):
        """Test that a subject has a type."""
        subject = Subject(self.DATA_MODEL, dict(type="type"), SUBJECT_ID, self.report)
        self.assertEqual("type", subject.type)

    def test_missing_type(self):
        """Test that a subject can have a missing type."""
        subject = Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report)
        self.assertEqual(None, subject.type)

    def test_instantiate_metrics(self):
        """Test that a subject instantiates its metrics."""
        subject = Subject(self.DATA_MODEL, dict(metrics={METRIC_ID: {}}), SUBJECT_ID, self.report)
        metric = Metric(self.DATA_MODEL, {}, METRIC_ID)
        self.assertEqual({METRIC_ID: metric}, subject.metrics_dict)

    def test_name(self):
        """Test that a subject has a name."""
        subject = Subject(self.DATA_MODEL, dict(name="Name"), SUBJECT_ID, self.report)
        self.assertEqual("Name", subject.name)

    def test_missing_name(self):
        """Test that a subject can have a missing name."""
        subject = Subject(self.DATA_MODEL, dict(type="software"), SUBJECT_ID, self.report)
        self.assertEqual("Software", subject.name)

    def test_tag_subject(self):
        """Test that a new subject can be created with metrics filtered by tag."""
        metric = Metric(self.DATA_MODEL, dict(tags=["tag"]), METRIC_ID)
        subject = Subject(
            self.DATA_MODEL,
            dict(name="Subject", metrics=({METRIC_ID: metric})),
            SUBJECT_ID,
            self.report,
        )
        tag_subject = subject.tag_subject("tag")
        self.assertEqual([metric], tag_subject.metrics)
        self.assertEqual("Report ❯ Subject", tag_subject.name)

    def test_tag_subject_with_unused_tag(self):
        """Test that filtering a subject's metrics by a non-existing tag returns None."""
        metric = Metric(self.DATA_MODEL, dict(tags=["tag"]), METRIC_ID)
        subject = Subject(
            self.DATA_MODEL,
            dict(name="Subject", metrics=({METRIC_ID: metric})),
            SUBJECT_ID,
            self.report,
        )
        self.assertIsNone(subject.tag_subject("unused"))

    def test_summarize(self):
        """Test that a subject can be summarized."""
        metric = Metric(self.DATA_MODEL, dict(type="violations"), METRIC_ID)
        subject = Subject(
            self.DATA_MODEL,
            dict(name="Subject", metrics=({METRIC_ID: metric})),
            SUBJECT_ID,
            self.report,
        )
        self.assertEqual(
            dict(
                name="Subject",
                metrics={
                    METRIC_ID: dict(
                        latest_measurement=None,
                        recent_measurements=[],
                        scale="count",
                        sources={},
                        status=None,
                        status_start=None,
                        type="violations",
                    )
                },
            ),
            subject.summarize({}),
        )
