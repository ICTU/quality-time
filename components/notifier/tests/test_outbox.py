""""Unit tests for the outbox."""

import unittest
from unittest.mock import patch

from models.metric_notification_data import MetricNotificationData
from models.notification import Notification
from outbox import Outbox


class OutboxTestCase(unittest.TestCase):
    """Unit tests for the outbox."""

    def setUp(self):
        """Set variables for the other testcases."""
        self.reason1 = "status_changed"
        self.data_model = dict(
            metrics=dict(metric_type=dict(name="type")),
            sources=dict(
                quality_time=dict(
                    parameters=dict(
                        status=dict(
                            api_values={"target met (green)": "target_met", "target not met (red)": "target_not_met"}
                        )
                    )
                )
            ),
        )
        self.report_url = "https://report1"
        self.report = dict(title="report_title", url=self.report_url)
        metric1 = dict(
            type="metric_type",
            name="default metric 1",
            unit="units",
            scale="count",
            recent_measurements=[
                dict(count=dict(value=10, status="target_met")),
                dict(count=dict(value=20, status="target_not_met")),
            ],
        )
        metric2 = dict(
            type="metric_type",
            name="default metric 2",
            unit="units",
            scale="count",
            recent_measurements=[
                dict(count=dict(value=10, status="target_met")),
                dict(count=dict(value=20, status="target_not_met")),
            ],
        )
        self.metric_notification_data1 = MetricNotificationData(metric1, self.data_model, self.reason1)
        self.metric_notification_data2 = MetricNotificationData(metric2, self.data_model, self.reason1)
        metrics1 = [self.metric_notification_data1, self.metric_notification_data2]
        metric3 = dict(
            type="metric_type",
            name="default metric 3",
            unit="units",
            scale="count",
            recent_measurements=[
                dict(count=dict(value=10, status="target_met")),
                dict(count=dict(value=20, status="target_not_met")),
            ],
        )
        metric4 = dict(
            type="metric_type",
            name="default metric 4",
            unit="units",
            scale="count",
            recent_measurements=[
                dict(count=dict(value=10, status="target_met")),
                dict(count=dict(value=20, status="target_not_met")),
            ],
        )
        metric_notification_data3 = MetricNotificationData(metric3, self.data_model, self.reason1)
        metric_notification_data4 = MetricNotificationData(metric4, self.data_model, self.reason1)
        metrics2 = [metric_notification_data3, metric_notification_data4]
        self.notifications = [
            Notification(self.report, metrics1, "uuid1", dict(teams_webhook="https://url/1")),
            Notification(self.report, metrics2, "uuid2", dict(teams_webhook="https://url/2")),
        ]

    def test_merge_notifications_into_nothing(self):
        """Test that notifications are merged, even if the outbox is currently empty."""
        outbox = Outbox()
        outbox.add_notifications(self.notifications)
        self.assertEqual(outbox.notifications, self.notifications)

    def test_merge_nothing_into_notifications(self):
        """Test that notifications are merged, even if no new metrics are given to be added."""
        outbox = Outbox(self.notifications)
        outbox.add_notifications([])
        self.assertEqual(outbox.notifications, self.notifications)

    def test_merge_nothing_into_nothing(self):
        """Test that notifications are merged, even if the destination is empty."""
        outbox = Outbox()
        outbox.add_notifications([])
        self.assertEqual(outbox.notifications, [])

    def test_merge_notifications_with_same_destination_but_different_report(self):
        """Test that the metrics are merged into the correct notification."""
        report = dict(title="different_title", url="https://differentreport")
        metric1 = dict(metric_name="new_metric 1")
        metric2 = dict(metric_name="new_metric 2")
        metrics1 = [metric1, metric2]
        new_notifications = [Notification(report, metrics1, "uuid1", {})]
        outbox = Outbox(self.notifications)
        outbox.add_notifications(new_notifications)
        self.assertEqual(
            outbox.notifications[0].metrics,
            [self.metric_notification_data1, self.metric_notification_data2],
        )

    def test_merge_notifications_with_same_destination(self):
        """Test that the metrics are merged into the correct notification."""
        report = dict(title="report_title", url="https://differentreport")
        metric1 = dict(metric_name="new metric 1")
        metric2 = dict(metric_name="new metric 2")
        metrics1 = [metric1, metric2]
        new_notifications = [Notification(report, metrics1, "uuid1", dict(teams_webhook="https://url/1"))]
        outbox = Outbox(self.notifications)
        outbox.add_notifications(new_notifications)
        self.assertEqual(
            outbox.notifications[0].metrics,
            [
                self.metric_notification_data1,
                self.metric_notification_data2,
                dict(metric_name="new metric 1"),
                dict(metric_name="new metric 2"),
            ],
        )

    @patch("models.notification.Notification.ready")
    @patch("outbox.send_notification_to_teams")
    def test_send_notifications(self, mocked_send, mocked_ready):
        """Test that notifications can be sent."""
        mocked_ready.side_effect = [True, False]
        outbox = Outbox(self.notifications)
        outbox.send_notifications()
        mocked_send.assert_called_once()

    @patch("models.notification.Notification.ready")
    def test_notifications_without_destination(self, mocked_ready):
        """Test that notifications without a destination aren't sent."""
        mocked_ready.side_effect = [True, True]
        notifications = self.notifications
        notifications[0].destination["teams_webhook"] = None
        notifications[1].destination["teams_webhook"] = None
        outbox = Outbox(notifications)
        self.assertEqual(0, outbox.send_notifications())

    @patch("models.notification.Notification.ready")
    @patch("outbox.send_notification_to_teams")
    def test_deletion_of_notifications(self, mocked_send, mocked_ready):
        """Test that notifications are deleted after sending."""
        mocked_ready.side_effect = [True, True]
        mocked_send.side_effect = [None, None]
        outbox = Outbox(self.notifications)
        self.assertEqual(2, outbox.send_notifications())
