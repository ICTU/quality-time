""""Unit tests for the notification strategies."""

import datetime
import unittest

from strategies.reds_that_are_new import reds_that_are_new


class MyTestCase(unittest.TestCase):
    """Unit tests for the 'amount of new red metrics per report' notification strategy."""

    def setUp(self):
        self.most_recent_measurement_seen = datetime.datetime.min.isoformat()

    def test_no_reports(self):
        """Test that there is nothing to notify when there are no reports."""
        self.assertEqual([], reds_that_are_new(dict(reports=[]), self.most_recent_measurement_seen))

    def test_no_red_metrics(self):
        """Test that there is nothing to notify when there are no red metrics."""
        green_metric = dict(status="target_met")
        subject1 = dict(metrics=dict(metric1=green_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])
        self.assertEqual([], reds_that_are_new(json, self.most_recent_measurement_seen))

    def test_old_red_metric(self):
        """Test that there is nothing to notify if the red metric was already red."""
        red_metric = dict(
            status="target_not_met",
            recent_measurements=[dict(start="2020-01-01T00:23:59+59:00", end="2020-02-01T00:23:59+59:00")])
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(report_uuid="report1", title="Title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])
        self.assertEqual([], reds_that_are_new(json, self.most_recent_measurement_seen))

    def test_red_metric_without_recent_measurements(self):
        """Test that there is nothing to notify if the red metric has no recent measurements."""
        red_metric1 = dict(status="target_not_met")
        red_metric2 = dict(status="target_not_met", recent_measurements=[])
        subject1 = dict(metrics=dict(metric1=red_metric1, metric2=red_metric2))
        report1 = dict(report_uuid="report1", title="Title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])
        self.assertEqual([], reds_that_are_new(json, self.most_recent_measurement_seen))

    def test_new_red_metric(self):
        """Test that the number of red metrics is returned."""
        equal_start_and_end_time = "2020-01-01T00:23:59+59:00"
        red_metric = dict(
            status="target_not_met",
            recent_measurements=[dict(start=equal_start_and_end_time, end=equal_start_and_end_time)])
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(
            report_uuid="report1", title="Title", teams_webhook="webhook", url="http://report1",
            subjects=dict(subject1=subject1))
        json = dict(reports=[report1])
        self.assertEqual(
            [dict(
                report_title="Title", report_uuid="report1", new_red_metrics=1, teams_webhook="webhook",
                url="http://report1")],
            reds_that_are_new(json, self.most_recent_measurement_seen))
