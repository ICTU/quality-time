""""Unit tests for the notification strategies."""

import datetime
import json
import pathlib
import unittest

from strategies.changed_status import get_notable_metrics_from_json, has_new_status


class StrategiesTestCase(unittest.TestCase):
    """Unit tests for the 'amount of new red metrics per report' notification strategy."""

    @classmethod
    def setUpClass(cls) -> None:
        """Provide the data_model to the class."""
        module_dir = pathlib.Path(__file__).resolve().parent
        data_model_path = module_dir.parent.parent.parent / "server" / "src" / "data" / "datamodel.json"
        with data_model_path.open() as json_data_model:
            cls.data_model = json.load(json_data_model)

    def setUp(self):
        """Set variables for the other testcases."""
        self.most_recent_measurement_seen = datetime.datetime.min.isoformat()
        self.first_timestamp = "2019-01-01T00:23:59+59:00"
        self.second_timestamp = "2020-01-01T00:23:59+59:00"
        self.report_url = "https://report1"
        self.white_status = "unknown"
        self.red_metric_status = "red (target not met)"
        self.green_metric_status = "green (target met)"

    def test_no_reports(self):
        """Test that there is nothing to notify when there are no reports."""
        self.assertEqual(
            [], get_notable_metrics_from_json(self.data_model, dict(reports=[]), self.most_recent_measurement_seen))

    def test_no_red_metrics(self):
        """Test that there is nothing to notify when there are no red metrics."""
        count = dict(status="target_met", value="0")
        green_metric = dict(
            status="target_met",
            scale="count",
            recent_measurements=[dict(start=self.first_timestamp, end=self.second_timestamp, count=count)])
        subject1 = dict(metrics=dict(metric1=green_metric))
        report1 = dict(report_uuid="report1", title="report_title", subjects=dict(subject1=subject1))
        reports_json = dict(reports=[report1])
        self.assertEqual(
            [], get_notable_metrics_from_json(self.data_model, reports_json, self.most_recent_measurement_seen))

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
        reports_json = dict(reports=[report1])
        self.assertEqual(
            [], get_notable_metrics_from_json(self.data_model, reports_json, self.most_recent_measurement_seen))

    def test_red_metric_without_recent_measurements(self):
        """Test that there is nothing to notify if the red metric has no recent measurements."""
        red_metric1 = dict(status="target_not_met", scale="count")
        red_metric2 = dict(status="target_not_met", scale="count", recent_measurements=[])
        subject1 = dict(metrics=dict(metric1=red_metric1, metric2=red_metric2))
        report1 = dict(report_uuid="report1", title="Title", subjects=dict(subject1=subject1))
        reports_json = dict(reports=[report1])
        self.assertEqual(
            [], get_notable_metrics_from_json(self.data_model, reports_json, self.most_recent_measurement_seen))

    def test_new_red_metric(self):
        """Test that a metric that has become red is included."""
        old_count = dict(status="target_met", value="5")
        new_count = dict(status="target_not_met", value="10")
        red_metric = dict(
            type="tests",
            name="metric1",
            scale="count",
            unit="units",
            status="target_not_met",
            recent_measurements=[
                dict(start=self.first_timestamp, end=self.second_timestamp, count=old_count),
                dict(start=self.second_timestamp, end=self.second_timestamp, count=new_count)])
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(
            title="Title", report_uuid="report1", teams_webhook="webhook", url=self.report_url,
            subjects=dict(subject1=subject1))
        reports_json = dict(reports=[report1])
        self.assertEqual(
            [dict(
                report_uuid="report1", report_title="Title", teams_webhook="webhook", url=self.report_url,
                metrics=[dict(
                    metric_type="tests",
                    metric_name="metric1",
                    metric_unit="units",
                    new_metric_status=self.red_metric_status,
                    new_metric_value="10",
                    old_metric_status=self.green_metric_status,
                    old_metric_value="5"
                )])],
            get_notable_metrics_from_json(self.data_model, reports_json, self.most_recent_measurement_seen))

    def test_new_red_metric_without_count_scale(self):
        """Test that a metric that doesn't have a count scale that has become red is included."""
        old_percentage = dict(status="target_met", value="5")
        new_percentage = dict(status="target_not_met", value="10")
        red_metric = dict(
            type="tests",
            name="",
            scale="percentage",
            unit="units",
            status="target_not_met",
            recent_measurements=[
                dict(start=self.first_timestamp, end=self.second_timestamp, percentage=old_percentage),
                dict(start=self.second_timestamp, end=self.second_timestamp, percentage=new_percentage)])
        subject1 = dict(metrics=dict(metric1=red_metric))
        report1 = dict(
            title="Title", report_uuid="report1", teams_webhook="webhook", url=self.report_url,
            subjects=dict(subject1=subject1))
        reports_json = dict(reports=[report1])
        self.assertEqual(
            [dict(
                report_uuid="report1", report_title="Title", teams_webhook="webhook", url=self.report_url,
                metrics=[dict(
                    metric_type="tests",
                    metric_name="Tests",
                    metric_unit="units",
                    new_metric_status=self.red_metric_status,
                    new_metric_value="10",
                    old_metric_status=self.green_metric_status,
                    old_metric_value="5"
                )])],
            get_notable_metrics_from_json(self.data_model, reports_json, self.most_recent_measurement_seen))

    def test_new_white_metric(self):
        """Test that a metric that turns white is added."""
        metric = dict(
            scale="count",
            status=self.white_status,
            recent_measurements=[
                dict(
                    start=self.second_timestamp,
                    count=dict(
                        status="target_met")),
                dict(
                    start=self.first_timestamp,
                    count=dict(
                        status=self.white_status))])
        result = has_new_status(metric, self.white_status,self.most_recent_measurement_seen)
        self.assertTrue(result)

    def test_old_white_metric(self):
        """Test that a metric that was already white isn't added."""
        metric = dict(
            scale="count",
            status=self.white_status,
            recent_measurements=[
                dict(
                    start=self.second_timestamp,
                    count=dict(
                        status=self.white_status)),
                dict(
                    start=self.first_timestamp,
                    count=dict(
                        status=self.white_status))])
        self.assertFalse(has_new_status(metric, self.white_status, self.most_recent_measurement_seen))

    def test_only_one_measurement(self):
        """Test that metrics with only one measurement (and therefore no changes in value) aren't added."""
        metric = dict(
            scale="count",
            status=self.white_status,
            recent_measurements=[
                dict(
                    start=self.first_timestamp,
                    count=dict(
                        status=self.white_status))])
        self.assertFalse(has_new_status(metric, self.white_status, self.most_recent_measurement_seen))

    def test_no_measurements(self):
        """Test that metrics with only one measurement (and therefore no changes in value) aren't added."""
        metric = dict(
            scale="count",
            status=self.white_status)
        self.assertFalse(has_new_status(metric, self.white_status, self.most_recent_measurement_seen))

    def test_multiple_reports_with_same_destination(self):
        """Test that the correct metrics are notified when multiple reports notify the same destination."""
        old_count = dict(status="target_met", value="5")
        new_count = dict(status="target_not_met", value="10")
        red_metric1 = dict(
            type="tests",
            name="metric1",
            scale="count",
            unit="units",
            status="target_not_met",
            recent_measurements=[
                dict(start=self.first_timestamp, end=self.second_timestamp, count=old_count),
                dict(start=self.second_timestamp, end=self.second_timestamp, count=new_count)])
        red_metric2 = dict(
            type="tests",
            name="metric2",
            scale="count",
            unit="units",
            status="target_met",
            recent_measurements=[
                dict(start=self.first_timestamp, end=self.second_timestamp, count=old_count),
                dict(start=self.second_timestamp, end=self.second_timestamp, count=new_count)])
        subject1 = dict(metrics=dict(metric1=red_metric1))
        subject2 = dict(metrics=dict(metric1=red_metric2))
        report1 = dict(
            title="Title", report_uuid="report1", teams_webhook="webhook", url=self.report_url,
            subjects=dict(subject1=subject1))
        report2 = dict(
            title="Title", report_uuid="report2", teams_webhook="webhook", url="https://report2",
            subjects=dict(subject1=subject2))
        reports_json = dict(reports=[report1, report2])
        self.assertEqual(
            [dict(
                report_uuid="report1", report_title="Title", teams_webhook="webhook", url=self.report_url,
                metrics=[dict(
                    metric_type="tests",
                    metric_name="metric1",
                    metric_unit="units",
                    new_metric_status=self.red_metric_status,
                    new_metric_value="10",
                    old_metric_status=self.green_metric_status,
                    old_metric_value="5"
                )])],
            get_notable_metrics_from_json(self.data_model, reports_json, self.most_recent_measurement_seen))
