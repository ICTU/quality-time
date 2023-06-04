"""Fixture for reports."""
import unittest
from typing import cast

from shared.utils.type import MetricId, NotificationDestinationId, SourceId, SubjectId

from .fixtures import create_report

METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination1")
SOURCE_ID = cast(SourceId, "source_uuid")
SUBJECT_ID = cast(SubjectId, "subject_uuid")


class FixtureTest(unittest.TestCase):
    """Tests for fixtures."""

    def test_create_report(self):
        """Tests create report."""
        report1 = create_report()
        self.assertEqual(report1["report_uuid"], "report1")
        self.assertEqual(report1["title"], "Title")
        self.assertEqual(report1["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["name"], "Metric")

    def test_create_report_deleted(self):
        """Tests with deleted."""
        report_deleted = create_report(deleted=True)
        self.assertTrue(report_deleted["deleted"])

    def test_create_report_with_title(self):
        """Tests with title."""
        report_with_alternate_title = create_report(title="Foo")
        self.assertEqual(report_with_alternate_title["title"], "Foo")

    def test_create_report_with_kwargs(self):
        """Tests with kwargs."""
        report_with_kwargs = create_report(last=True, metric_id=METRIC_ID2)
        self.assertTrue(report_with_kwargs["last"])
        self.assertIsNotNone(report_with_kwargs["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2])

    def test_create_report_with_other_kwargs(self):
        """Tests with other kwargs."""
        report_with_kwargs = create_report(source_type="violations", metric_type="foo")
        self.assertEqual(
            report_with_kwargs["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["type"],
            "violations",
        )
        self.assertEqual(report_with_kwargs["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["type"], "foo")

    def test_create_report_with_wrong_kwargs(self):
        """Tests with wrong kwargs."""
        with self.assertRaises(ValueError):
            create_report(foo="bar")
