""""Unit tests for the notification strategies."""

import datetime
import unittest

from strategies.reds_that_are_new import get_notable_metrics_from_json


class StrategiesTestCase(unittest.TestCase):
    """Unit tests for the 'amount of new red metrics per report' notification strategy."""

    def setUp(self):
        """Set variables for the other testcases."""
        self.most_recent_measurement_seen = datetime.datetime.min.isoformat()
        self.first_timestamp = "2019-01-01T00:23:59+59:00"
        self.second_timestamp = "2020-01-01T00:23:59+59:00"

    def test_no_reports(self):
        """Test that there is nothing to notify when there are no reports."""
        self.assertEqual([], get_notable_metrics_from_json(dict(reports=[]), self.most_recent_measurement_seen))

    def test_no_red_metrics(self):
        """Test that there is nothing to notify when there are no red metrics."""
        green_metric = dict(status="target_met")
        subject1 = dict(metrics=dict(metric1=green_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])
        self.assertEqual([], get_notable_metrics_from_json(json, self.most_recent_measurement_seen))

    def test_old_red_metric(self):
        """Test that there is nothing to notify if the red metric was already red."""
        count = dict(status="target_not_met", value="10")
        red_metric = dict(
            type="test",
            name="metric1",
            scale="count",
            unit="units",
            status="target_not_met",
            recent_measurements=[dict(start=self.first_timestamp, end=self.second_timestamp, count=count)])
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(report_uuid="report1", title="Title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])
        self.assertEqual([], get_notable_metrics_from_json(json, self.most_recent_measurement_seen))

    def test_red_metric_without_recent_measurements(self):
        """Test that there is nothing to notify if the red metric has no recent measurements."""
        red_metric1 = dict(status="target_not_met")
        red_metric2 = dict(status="target_not_met", recent_measurements=[])
        subject1 = dict(metrics=dict(metric1=red_metric1, metric2=red_metric2))
        report1 = dict(report_uuid="report1", title="Title", subjects=dict(subject1=subject1))
        json = dict(reports=[report1])
        self.assertEqual([], get_notable_metrics_from_json(json, self.most_recent_measurement_seen))

    def test_new_red_metric(self):
        """Test that a metric that has become red is included."""
        old_count = dict(status="target_met", value="5")
        new_count = dict(status="target_not_met", value="10")
        red_metric = dict(
            type="test",
            name="metric1",
            scale="count",
            unit="units",
            status="target_not_met",
            recent_measurements=[
                dict(start=self.first_timestamp, end=self.second_timestamp, count=old_count),
                dict(start=self.second_timestamp, end=self.second_timestamp, count=new_count)])
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(
            title="Title", report_uuid="report1", teams_webhook="webhook", url="http://report1",
            subjects=dict(subject1=subject1))
        json = dict(reports=[report1])
        self.assertEqual(
            [dict(
                report_uuid="report1", report_title="Title",
                teams_webhook="webhook", url="http://report1",
                new_red_metrics=1, metrics=[dict(
                    metric_type="test",
                    metric_name="metric1",
                    metric_unit="units",
                    new_metric_status="target_not_met",
                    new_metric_value="10",
                    old_metric_status="target_met",
                    old_metric_value="5"
                )])],
            get_notable_metrics_from_json(json, self.most_recent_measurement_seen))

    def test_new_red_metric_without_count_scale(self):
        """Test that a metric that doesn't have a count scale that has become red is included."""
        old_percentage = dict(status="target_met", value="5")
        new_percentage = dict(status="target_not_met", value="10")
        red_metric = dict(
            type="test",
            name="metric1",
            scale="percentage",
            unit="units",
            status="target_not_met",
            recent_measurements=[
                dict(start=self.first_timestamp, end=self.second_timestamp, percentage=old_percentage),
                dict(start=self.second_timestamp, end=self.second_timestamp, percentage=new_percentage)])
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(
            title="Title", report_uuid="report1", teams_webhook="webhook", url="http://report1",
            subjects=dict(subject1=subject1))
        json = dict(reports=[report1])
        self.assertEqual(
            [dict(
                report_uuid="report1", report_title="Title",
                teams_webhook="webhook", url="http://report1",
                new_red_metrics=1, metrics=[dict(
                    metric_type="test",
                    metric_name="metric1",
                    metric_unit="units",
                    new_metric_status="target_not_met",
                    new_metric_value="10",
                    old_metric_status="target_met",
                    old_metric_value="5"
                )])],
            get_notable_metrics_from_json(json, self.most_recent_measurement_seen))
