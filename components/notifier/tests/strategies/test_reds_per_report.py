"""Unit tests for the notification strategies."""

import unittest

from strategies.reds_per_report import reds_per_report


class RedsPerReportTestCase(unittest.TestCase):
    """Unit tests for the reds per report notification strategy."""

    def test_no_reports(self):
        """Test that there is nothing to notify when there are no reports."""
        self.assertEqual([], reds_per_report(dict(reports=[])))

    def test_no_red_metrics(self):
        """Test that there is nothing to notify when there are no red metrics."""
        green_metric = dict(status="target_met")
        subject1 = dict(metrics=dict(metric1=green_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])

        result = reds_per_report(json)[0]

        self.assertEqual(["report_title", 0], [result["report_title"], result["red_metrics"]])

    def test_red_metrics(self):
        """Test that the number of red metrics is returned."""
        red_metric = dict(status="target_not_met")
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])

        result = reds_per_report(json)[0]

        self.assertEqual(["report_title", 1], [result["report_title"], result["red_metrics"]])
