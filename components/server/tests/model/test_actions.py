"""Unit tests for the model actions."""


import unittest

from model.actions import copy_metric, copy_report, copy_source, copy_subject
from server_utilities.type import ReportId


class CopySourceTest(unittest.TestCase):
    """Unit tests for the copy source action."""
    def test_copy_name(self):
        """Test that the copy name is changed."""
        source_copy = copy_source(dict(name="Source"), {})
        self.assertEqual("Source (copy)", source_copy["name"])

    def test_copy_without_name(self):
        """Test that the copy name is based on the data model if the original source doesn't have a name."""
        source_copy = copy_source(dict(type="source_type"), dict(sources=dict(source_type=dict(name="Source type"))))
        self.assertEqual("Source type (copy)", source_copy["name"])

    def test_copy_without_name_change(self):
        """Test that the copy name can be left unchanged."""
        source_copy = copy_source(dict(name="Source"), {}, change_name=False)
        self.assertEqual("Source", source_copy["name"])


class CopyMetricTest(unittest.TestCase):
    """Unit tests for the copy metric action."""
    def test_copy_name(self):
        """Test that the copy name is changed."""
        metric_copy = copy_metric(dict(name="Metric", sources={}), {})
        self.assertEqual("Metric (copy)", metric_copy["name"])

    def test_copy_without_name(self):
        """Test that the copy name is based on the data model if the original metric doesn't have a name."""
        metric_copy = copy_metric(
            dict(type="metric_type", sources={}), dict(metrics=dict(metric_type=dict(name="Metric type"))))
        self.assertEqual("Metric type (copy)", metric_copy["name"])

    def test_copy_without_name_change(self):
        """Test that the copy name can be left unchanged."""
        metric_copy = copy_metric(dict(name="Metric", sources={}), {}, change_name=False)
        self.assertEqual("Metric", metric_copy["name"])

    def test_copy_report_uuid(self):
        """Test that the report UUID can be changed."""
        metric_copy = copy_metric(dict(name="Metric", sources={}), {}, report_uuid=ReportId("new report uuid"))
        self.assertEqual("new report uuid", metric_copy["report_uuid"])

    def test_copy_sources(self):
        """Test that the sources are copied too."""
        metric_copy = copy_metric(dict(name="Metric", sources=dict(source_uuid=dict(name="Source"))), {})
        self.assertEqual("Source", list(metric_copy["sources"].values())[0]["name"])


class CopySubjectTest(unittest.TestCase):
    """Unit tests for the copy subject action."""
    def test_copy_name(self):
        """Test that the copy name is changed."""
        subject_copy = copy_subject(dict(name="Subject", metrics={}), {})
        self.assertEqual("Subject (copy)", subject_copy["name"])

    def test_copy_without_name(self):
        """Test that the copy name is based on the data model if the original subject doesn't have a name."""
        subject_copy = copy_subject(
            dict(type="subject_type", metrics={}), dict(subjects=dict(subject_type=dict(name="Subject type"))))
        self.assertEqual("Subject type (copy)", subject_copy["name"])

    def test_copy_without_name_change(self):
        """Test that the copy name can be left unchanged."""
        subject_copy = copy_subject(dict(name="Subject", metrics={}), {}, change_name=False)
        self.assertEqual("Subject", subject_copy["name"])

    def test_copy_metrics(self):
        """Test that the metrics are copied too."""
        subject_copy = copy_subject(dict(name="Subject", metrics=dict(metric_uuid=dict(name="Metric", sources={}))), {})
        self.assertEqual("Metric", list(subject_copy["metrics"].values())[0]["name"])


class CopyReportTest(unittest.TestCase):
    """Unit tests for the copy report action."""
    def test_copy_title(self):
        """Test that the copy title is changed."""
        report_copy = copy_report(dict(title="Report", subjects={}), {}, ReportId("new report uuid"))
        self.assertEqual("Report (copy)", report_copy["title"])

    def test_copy_report_uuid(self):
        """Test that the report UUID can be changed."""
        report_copy = copy_report(dict(title="Report", subjects={}), {}, ReportId("new report uuid"))
        self.assertEqual("new report uuid", report_copy["report_uuid"])

    def test_copy_subjects(self):
        """Test that the subjects are copied too."""
        report_copy = copy_report(
            dict(title="Report", subjects=dict(subject_uuid=dict(name="Subject", metrics={}))), {},
            ReportId("new report uuid"))
        self.assertEqual("Subject", list(report_copy["subjects"].values())[0]["name"])
