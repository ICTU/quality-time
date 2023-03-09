""""Unit tests for the notification strategies."""

from datetime import datetime, timezone
import unittest

from strategies.notification_strategy import NotificationFinder


class StrategiesTests(unittest.TestCase):
    """Unit tests for the 'number of new red metrics per report' notification strategy."""

    OLD_TIMESTAMP = "2019-01-01T00:00:00+00:00"
    NEW_TIMESTAMP = "2020-01-01T00:00:00+00:00"

    def setUp(self):
        """Override to create a reports JSON fixture."""
        self.notification_finder = NotificationFinder()
        self.most_recent_measurement_seen = datetime.min.replace(tzinfo=timezone.utc)
        self.white_metric_status = "unknown"
        self.red_metric = self.metric(name="metric1", status="target_not_met")
        self.red_metric_measurements = [
            dict(
                metric_uuid="red_metric",
                start=self.OLD_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count=dict(status="target_met", value="5"),
            ),
            dict(
                metric_uuid="red_metric",
                start=self.NEW_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count=dict(status="target_not_met", value="10"),
            ),
        ]
        self.reports = [
            dict(
                report_uuid="report1",
                title="Title",
                subjects=dict(subject1=dict(metrics=dict(red_metric=self.red_metric), type="software")),
                notification_destinations=dict(destination_uuid=dict(name="destination")),
            )
        ]

    @staticmethod
    def metric(name="metric1", status="target_met", scale="count", recent_measurements=None, status_start=None):
        """Create a metric."""
        return dict(
            name=name,
            scale=scale,
            status=status,
            type="tests",
            unit="units",
            recent_measurements=recent_measurements or [],
            status_start=status_start or "",
        )

    def get_notifications(self, measurements=None):
        """Return the notifications."""
        return self.notification_finder.get_notifications(
            self.reports, measurements or [], self.most_recent_measurement_seen
        )

    def test_no_reports(self):
        """Test that there is nothing to notify when there are no reports."""
        self.reports = []
        self.assertEqual([], self.get_notifications())

    def test_no_red_metrics(self):
        """Test that there is nothing to notify when there are no red metrics."""
        green_metric = self.metric(
            recent_measurements=[
                dict(start=self.OLD_TIMESTAMP, end=self.NEW_TIMESTAMP, count=dict(status="target_met", value="0"))
            ]
        )
        self.reports[0]["subjects"]["subject1"]["metrics"] = dict(metric=green_metric)
        self.assertEqual([], self.get_notifications())

    def test_old_red_metric(self):
        """Test that there is nothing to notify if the red metric was already red."""
        self.red_metric_measurements[0]["count"]["status"] = "target_not_met"
        self.assertEqual([], self.get_notifications())

    def test_red_metric_without_recent_measurements(self):
        """Test that there is nothing to notify if the red metric has no recent measurements."""
        self.red_metric_measurements = []
        self.assertEqual([], self.get_notifications())

    def test_new_red_metric(self):
        """Test that a metric that has become red is included."""
        notifications = self.get_notifications(self.red_metric_measurements)
        self.assertEqual(
            ["metric1", "red (target not met)"],
            [notifications[0].metrics[0].metric_name, notifications[0].metrics[0].new_metric_status],
        )

    def test_new_red_metric_without_count_scale(self):
        """Test that a metric that doesn't have a count scale that became red is included."""
        self.assertEqual(["metric1"], [self.get_notifications(self.red_metric_measurements)[0].metrics[0].metric_name])

    def test_recently_changed_metric_status(self):
        """Test that a metric that turns white is added."""
        metric = self.metric(status=self.white_metric_status)
        measurements = [
            dict(
                metric_uuid="metric_uuid",
                start=self.NEW_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count=dict(status="target_met"),
            ),
            dict(
                metric_uuid="metric_uuid",
                start=self.OLD_TIMESTAMP,
                end=self.OLD_TIMESTAMP,
                count=dict(status=self.white_metric_status),
            ),
        ]
        self.assertTrue(
            self.notification_finder.status_changed(metric, measurements, self.most_recent_measurement_seen)
        )

    def test_new_measurement_same_status(self):
        """Test that a metric that was already white isn't added."""
        metric = self.metric(status=self.white_metric_status)
        measurements = [
            dict(start=self.NEW_TIMESTAMP, count=dict(status=self.white_metric_status)),
            dict(start=self.OLD_TIMESTAMP, count=dict(status=self.white_metric_status)),
        ]
        self.assertFalse(
            self.notification_finder.status_changed(metric, measurements, self.most_recent_measurement_seen)
        )

    def test_no_change_due_to_only_one_measurement(self):
        """Test that metrics with only one measurement (and therefore no changes in value) aren't added."""
        metric = self.metric(status=self.white_metric_status)
        self.assertFalse(self.notification_finder.status_changed(metric, [{}], self.most_recent_measurement_seen))

    def test_no_change_due_to_no_measurements(self):
        """Test that metrics without measurements (and therefore no changes in value) aren't added."""
        metric = self.metric(status=self.white_metric_status)
        self.assertFalse(self.notification_finder.status_changed(metric, [], self.most_recent_measurement_seen))

    def test_multiple_reports_with_same_destination(self):
        """Test that the correct metrics are notified when multiple reports notify the same destination."""
        red_metric2 = self.red_metric.copy()
        red_metric2["name"] = "metric2"
        subject2 = dict(metrics=dict(metric1=red_metric2), type="software")
        report2 = dict(
            title="Title",
            report_uuid="report2",
            webhook="webhook",
            subjects=dict(subject=subject2),
            notification_destinations=dict(uuid1=dict(url="https://report2", name="destination2")),
        )
        self.reports.append(report2)
        red_metric2_measurements = [
            dict(
                metric_uuid="metric1",
                start=self.OLD_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count=dict(status="target_met", value="5"),
            ),
            dict(
                metric_uuid="metric1",
                start=self.NEW_TIMESTAMP,
                end=self.NEW_TIMESTAMP,
                count=dict(status="target_not_met", value="10"),
            ),
        ]
        metrics = []
        for notification in self.get_notifications(self.red_metric_measurements + red_metric2_measurements):
            metrics.append(notification.metrics)
        self.assertEqual(["metric1", "metric2"], [metrics[0][0].metric_name, metrics[1][0].metric_name])

    def test_no_notification_destinations_configured(self):
        """Test that no notification is to be sent if there are no configurations in notification destinations."""
        self.reports[0]["notification_destinations"] = {}
        self.assertEqual([], self.get_notifications())

    def test_no_notification_destinations_in_json(self):
        """Test that no notification is to be sent if notification destinations do not exist in the data."""
        del self.reports[0]["notification_destinations"]
        self.assertEqual([], self.get_notifications())
