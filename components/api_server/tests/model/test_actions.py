"""Unit tests for the model actions."""

import unittest
from typing import cast

from shared.model.metric import Metric
from shared.model.source import Source
from shared.model.subject import Subject
from shared.utils.functions import first
from shared.utils.type import MetricId, SourceId, SubjectId

from model.actions import copy_metric, copy_report, copy_source, copy_subject
from model.report import Report


class CopySourceTest(unittest.TestCase):
    """Unit tests for the copy source action."""

    def setUp(self):
        """Override to set up the source under test."""
        self.source_uuid = cast(SourceId, "source_uuid")
        self.source = cast(Source, {"name": "Source", "type": "pip"})

    def test_copy_name(self):
        """Test that the copy name is not changed."""
        source_copy = copy_source(self.source_uuid, self.source)
        self.assertEqual("Source", source_copy["name"])

    def test_copy_without_name(self):
        """Test that the copy name is not changed."""
        self.source["name"] = ""
        source_copy = copy_source(self.source_uuid, self.source)
        self.assertEqual("", source_copy["name"])


class CopyMetricTest(unittest.TestCase):
    """Unit tests for the copy metric action."""

    def setUp(self):
        """Override to set up the metric under test."""
        self.metric_uuid = cast(MetricId, "source_uuid")
        self.metric = cast(
            Metric,
            {
                "name": "Metric",
                "type": "security_warnings",
                "sources": {"source_uuid": {"type": "owasp_zap", "name": "Source"}},
            },
        )

    def test_copy_name(self):
        """Test that the copy name is not changed."""
        metric_copy = copy_metric(self.metric_uuid, self.metric)
        self.assertEqual("Metric", metric_copy["name"])

    def test_copy_without_name(self):
        """Test that the copy name is not changed."""
        self.metric["name"] = ""
        metric_copy = copy_metric(self.metric_uuid, self.metric)
        self.assertEqual("", metric_copy["name"])

    def test_copy_sources(self):
        """Test that the sources are copied too."""
        metric_copy = copy_metric(self.metric_uuid, self.metric)
        self.assertEqual("Source", first(metric_copy["sources"].values())["name"])


class CopySubjectTest(unittest.TestCase):
    """Unit tests for the copy subject action."""

    def setUp(self):
        """Override to set up the subject under test."""
        self.subject_uuid = cast(SubjectId, "subject_uuid")
        self.subject = cast(
            Subject,
            {
                "type": "software",
                "name": "Subject",
                "metrics": {"metric_uuid": {"type": "violations", "name": "Metric", "sources": {}}},
            },
        )

    def test_copy_name(self):
        """Test that the copy name is not changed."""
        subject_copy = copy_subject(self.subject_uuid, self.subject)
        self.assertEqual("Subject", subject_copy["name"])

    def test_copy_without_name(self):
        """Test that the copy name is not changed."""
        self.subject["name"] = ""
        subject_copy = copy_subject(self.subject_uuid, self.subject)
        self.assertEqual("", subject_copy["name"])

    def test_copy_metrics(self):
        """Test that the metrics are copied too."""
        subject_copy = copy_subject(self.subject_uuid, self.subject)
        self.assertEqual("Metric", first(subject_copy["metrics"].values())["name"])


class CopyReportTest(unittest.TestCase):
    """Unit tests for the copy report action."""

    def setUp(self):
        """Override to set up the report under test."""
        self.report = Report(
            {},
            {
                "report_uuid": "report_uuid",
                "title": "Report",
                "subjects": {"subject_uuid": {"name": "Subject", "type": "software", "metrics": {}}},
            },
        )

    def test_copy_title(self):
        """Test that the copy title is not changed."""
        report_copy = copy_report(self.report)
        self.assertEqual("Report", report_copy["title"])

    def test_copy_report_uuid(self):
        """Test that the report UUID can be changed."""
        report_copy = copy_report(self.report)
        self.assertNotEqual(self.report["report_uuid"], report_copy["report_uuid"])

    def test_copy_subjects(self):
        """Test that the subjects are copied too."""
        report_copy = copy_report(self.report)
        self.assertEqual("Subject", first(report_copy["subjects"].values())["name"])
