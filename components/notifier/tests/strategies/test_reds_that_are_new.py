""""Unit tests for the notification strategies."""

import unittest

from strategies.reds_that_are_new import reds_that_are_new


class MyTestCase(unittest.TestCase):
    """Unit tests for the 'amount of new red metrics per report' notification strategy."""

    def test_no_reports(self):
        """Test that there is nothing to notify when there are no reports."""
        self.assertEqual([], reds_that_are_new(dict(reports=[])))

    def test_no_new_red_metrics(self):
        """Test that there is nothing to notify when there are no red metrics."""
        old_status = dict(status="target_met")
        recent_measurement1 = [dict(count=old_status)]
        green_metric = dict(status="target_met", recent_measurements=recent_measurement1)
        subject1 = dict(metrics=dict(metric1=green_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])

        result = reds_that_are_new(json)[0]

        self.assertEqual(["report_title", 0], [result["report_title"], result["new_red_metrics"]])

    def test_still_red_metric(self):
        """Test that the number of red metrics is returned."""
        old_status = dict(status="target_not_met")
        recent_measurement1 = [dict(count=old_status)]
        red_metric = dict(status="target_not_met", recent_measurements=recent_measurement1)
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])

        result = reds_that_are_new(json)[0]

        self.assertEqual(["report_title", 0], [result["report_title"], result["new_red_metrics"]])

    def test_new_red_metrics(self):
        """Test that the number of red metrics is returned."""
        old_status = dict(status="target_met")
        recent_measurement1 = [dict(count=old_status)]
        red_metric = dict(status="target_not_met", recent_measurements=recent_measurement1)
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])

        result = reds_that_are_new(json)[0]

        self.assertEqual(["report_title", 1], [result["report_title"], result["new_red_metrics"]])

    def test_no_recent_measurements_on_red_metric(self):
        """"Test that reds are counted if no previous data is available"""
        red_metric = dict(status="target_not_met")
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])

        result = reds_that_are_new(json)[0]

        self.assertEqual(["report_title", 1], [result["report_title"], result["new_red_metrics"]])

    def test_no_recent_measurements_on_non_red_metric(self):
        """"Test that non reds are not counted if no recent measurements are available"""
        green_metric = dict(status="target_met")
        subject1 = dict(metrics=dict(metric1=green_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])

        result = reds_that_are_new(json)[0]

        self.assertEqual(["report_title", 0], [result["report_title"], result["new_red_metrics"]])
