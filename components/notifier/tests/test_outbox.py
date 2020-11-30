""""Unit tests for the outbox."""

import unittest
from unittest.mock import patch

from notification import Notification
from outbox import merge_notifications, send_notifications


class OutboxTestCase(unittest.TestCase):
    """Unit tests for the outbox."""

    def setUp(self):
        """Set variables for the other testcases."""
        self.report_url = "https://report1"
        self.red_metric_status = "red (target not met)"
        self.green_metric_status = "green (target met)"
        self.report = dict(title="report_title", url=self.report_url)
        metric1 = dict(
            metric_name="default metric 1",
            metric_unit="units",
            new_metric_value=20,
            old_metric_value=10,
            new_metric_status=self.red_metric_status,
            old_metric_status=self.green_metric_status,
        )
        metric2 = dict(
            metric_name="default metric 2",
            metric_unit="units",
            new_metric_value=20,
            old_metric_value=10,
            new_metric_status=self.red_metric_status,
            old_metric_status=self.green_metric_status,
        )
        metrics1 = [metric1, metric2]
        metric3 = dict(
            metric_name="default metric 3",
            metric_unit="units",
            new_metric_value=20,
            old_metric_value=10,
            new_metric_status=self.red_metric_status,
            old_metric_status=self.green_metric_status,
        )
        metric4 = dict(
            metric_name="default metric 4",
            metric_unit="units",
            new_metric_value=20,
            old_metric_value=10,
            new_metric_status=self.red_metric_status,
            old_metric_status=self.green_metric_status,
        )
        metrics2 = [metric3, metric4]
        self.notifications = [
            Notification(self.report, metrics1, "uuid1", dict(teams_webhook="https://url/1")),
            Notification(self.report, metrics2, "uuid2", dict(teams_webhook="https://url/2")),
        ]

    def test_merge_notifications_into_nothing(self):
        """Test that notifications are merged, even if the destination is empty."""
        self.assertEqual(merge_notifications([], self.notifications), self.notifications)

    def test_merge_nothing_into_notifications(self):
        """Test that notifications are merged, even if the destination is empty."""
        self.assertEqual(merge_notifications(self.notifications, []), self.notifications)

    def test_merge_nothing_into_nothing(self):
        """Test that notifications are merged, even if the destination is empty."""
        self.assertEqual(merge_notifications([], []), [])

    def test_merge_notifications_with_same_destination_but_different_report(self):
        """Test that the metrics are merged into the correct notification."""
        report = dict(title="different_title", url="https://differentreport")
        metric1 = dict(metric_name="new metric 1")
        metric2 = dict(metric_name="new metric 2")
        metrics1 = [metric1, metric2]
        new_notifications = [Notification(report, metrics1, "uuid1", {})]
        self.assertEqual(
            merge_notifications(self.notifications, new_notifications)[0].metrics,
            [
                dict(
                    metric_name="default metric 1",
                    metric_unit="units",
                    new_metric_value=20,
                    old_metric_value=10,
                    new_metric_status=self.red_metric_status,
                    old_metric_status=self.green_metric_status,
                ),
                dict(
                    metric_name="default metric 2",
                    metric_unit="units",
                    new_metric_value=20,
                    old_metric_value=10,
                    new_metric_status=self.red_metric_status,
                    old_metric_status=self.green_metric_status,
                ),
                dict(metric_name="new metric 1"),
                dict(metric_name="new metric 2"),
            ],
        )

    @patch("notification.Notification.ready")
    @patch("outbox.send_notification_to_teams")
    def test_send_notifications(self, mocked_send, mocked_ready):
        """Test that notifications can be sent."""
        mocked_ready.side_effect = [True, False]

        send_notifications(self.notifications)
        mocked_send.assert_called_once()

    @patch("notification.Notification.ready")
    def test_notifications_without_destination(self, mocked_ready):
        """Test that notifications without a destination aren't sent."""
        mocked_ready.side_effect = [True, True]
        notifications = self.notifications
        notifications[0].destination["teams_webhook"] = None
        notifications[1].destination["teams_webhook"] = None

        self.assertEqual(notifications, send_notifications(notifications))

    @patch("notification.Notification.ready")
    @patch("outbox.send_notification_to_teams")
    def test_deletion_of_notifications(self, mocked_send, mocked_ready):
        """Test that notifications are deleted after sending."""
        mocked_ready.side_effect = [True, True]
        mocked_send.side_effect = [None, None]

        self.assertEqual([], send_notifications(self.notifications))
