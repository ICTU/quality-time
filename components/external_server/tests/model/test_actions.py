"""Unit tests for the model actions."""

import unittest

from model.actions import copy_metric, copy_report, copy_source, copy_subject


class CopySourceTest(unittest.TestCase):
    """Unit tests for the copy source action."""

    def setUp(self):
        """Override to set up the data model and source under test."""
        self.data_model = dict(sources=dict(source_type=dict(name="Source type")))
        self.source = dict(name="Source", type="source_type")

    def test_copy_name(self):
        """Test that the copy name is changed."""
        source_copy = copy_source(self.source, self.data_model)
        self.assertEqual("Source (copy)", source_copy["name"])

    def test_copy_without_name(self):
        """Test that the copy name is based on the data model if the original source doesn't have a name."""
        self.source["name"] = ""
        source_copy = copy_source(self.source, self.data_model)
        self.assertEqual("Source type (copy)", source_copy["name"])

    def test_copy_without_name_change(self):
        """Test that the copy name can be left unchanged."""
        source_copy = copy_source(self.source, self.data_model, change_name=False)
        self.assertEqual("Source", source_copy["name"])


class CopyMetricTest(unittest.TestCase):
    """Unit tests for the copy metric action."""

    def setUp(self):
        """Override to set up the data model and metric under test."""
        self.data_model = dict(
            metrics=dict(metric_type=dict(name="Metric type")), sources=dict(source_type=dict(name="Source type"))
        )
        self.metric = dict(
            name="Metric", type="metric_type", sources=dict(source_uuid=dict(type="source_type", name="Source"))
        )

    def test_copy_name(self):
        """Test that the copy name is changed."""
        metric_copy = copy_metric(self.metric, self.data_model)
        self.assertEqual("Metric (copy)", metric_copy["name"])

    def test_copy_without_name(self):
        """Test that the copy name is based on the data model if the original metric doesn't have a name."""
        self.metric["name"] = ""
        metric_copy = copy_metric(self.metric, self.data_model)
        self.assertEqual("Metric type (copy)", metric_copy["name"])

    def test_copy_without_name_change(self):
        """Test that the copy name can be left unchanged."""
        metric_copy = copy_metric(self.metric, self.data_model, change_name=False)
        self.assertEqual("Metric", metric_copy["name"])

    def test_copy_sources(self):
        """Test that the sources are copied too."""
        metric_copy = copy_metric(self.metric, self.data_model)
        self.assertEqual("Source", list(metric_copy["sources"].values())[0]["name"])


class CopySubjectTest(unittest.TestCase):
    """Unit tests for the copy subject action."""

    def setUp(self):
        """Override to set up the data model and the subject under test."""
        self.data_model = dict(
            subjects=dict(subject_type=dict(name="Subject type")), metrics=dict(metric_type=dict(name="Metric type"))
        )
        self.subject = dict(
            type="subject_type",
            name="Subject",
            metrics=dict(metric_uuid=dict(type="metric_type", name="Metric", sources={})),
        )

    def test_copy_name(self):
        """Test that the copy name is changed."""
        subject_copy = copy_subject(self.subject, self.data_model)
        self.assertEqual("Subject (copy)", subject_copy["name"])

    def test_copy_without_name(self):
        """Test that the copy name is based on the data model if the original subject doesn't have a name."""
        self.subject["name"] = ""
        subject_copy = copy_subject(self.subject, self.data_model)
        self.assertEqual("Subject type (copy)", subject_copy["name"])

    def test_copy_without_name_change(self):
        """Test that the copy name can be left unchanged."""
        subject_copy = copy_subject(self.subject, self.data_model, change_name=False)
        self.assertEqual("Subject", subject_copy["name"])

    def test_copy_metrics(self):
        """Test that the metrics are copied too."""
        subject_copy = copy_subject(self.subject, self.data_model)
        self.assertEqual("Metric", list(subject_copy["metrics"].values())[0]["name"])


class CopyReportTest(unittest.TestCase):
    """Unit tests for the copy report action."""

    def setUp(self):
        """Override to set up the data model and report under test."""
        self.data_model = dict(subjects=dict(subject_type=dict(name="Subject type")))
        self.report = dict(
            report_uuid="report_uuid",
            title="Report",
            subjects=dict(subject_uuid=dict(name="Subject", type="subject_type", metrics={})),
        )

    def test_copy_title(self):
        """Test that the copy title is changed."""
        report_copy = copy_report(self.report, self.data_model)
        self.assertEqual("Report (copy)", report_copy["title"])

    def test_copy_report_uuid(self):
        """Test that the report UUID can be changed."""
        report_copy = copy_report(self.report, self.data_model)
        self.assertNotEqual(self.report["report_uuid"], report_copy["report_uuid"])

    def test_copy_subjects(self):
        """Test that the subjects are copied too."""
        report_copy = copy_report(self.report, self.data_model)
        self.assertEqual("Subject", list(report_copy["subjects"].values())[0]["name"])
