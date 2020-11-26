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
        self.report = dict(title="report_title", url=self.report_url)
        metric1 = dict(metric_name="default metric 1")
        metric2 = dict(metric_name="default metric 2")
        metrics1 = [metric1, metric2]
        metric3 = dict(metric_name="default metric 3")
        metric4 = dict(metric_name="default metric 4")
        metrics2 = [metric3, metric4]
        self.notifications = [
            Notification(self.report, metrics1, "uuid1", dict(teams_webhook="http://url/1")),
            Notification(self.report, metrics2, "uuid2", dict(teams_webhook="http://url/2"))]

    def test_merge_notifications_into_nothing(self):
        """Test that notifications are merged, even if the destination is empty."""
        self.assertEqual(merge_notifications(self.notifications, []), self.notifications)

    def test_merge_notifications_with_same_destination_but_different_report(self):
        """Test that the metrics are merged into the correct notification."""
        report = dict(title="different_title", url="https://differentreport")
        metric1 = dict(metric_name="new metric 1")
        metric2 = dict(metric_name="new metric 2")
        metrics1 = [metric1, metric2]
        new_notifications = [Notification(report, metrics1, "uuid1", {})]
        self.assertEqual(merge_notifications(new_notifications, self.notifications)[0].metrics,
                         [dict(metric_name="default metric 1"),
                          dict(metric_name="default metric 2"),
                          dict(metric_name="new metric 1"),
                          dict(metric_name="new metric 2")])

    @patch('notification.Notification.not_ready')
    @patch('outbox.send_notification_to_teams')
    def test_send_notifications(self, mocked_send, mocked_ready):
        """Test that notifications can be send."""
        mocked_ready.side_effect = [False, True]
        self.notifications[0].metrics[0]["metric_unit"]="units"
        self.notifications[0].metrics[0]["new_metric_value"]=20
        self.notifications[0].metrics[0]["old_metric_value"]=10
        self.notifications[0].metrics[0]["new_metric_status"]="red (target not met)"
        self.notifications[0].metrics[0]["old_metric_status"]="green (target met)"

        self.notifications[0].metrics[1]["metric_unit"]="units"
        self.notifications[0].metrics[1]["new_metric_value"]=20
        self.notifications[0].metrics[1]["old_metric_value"]=10
        self.notifications[0].metrics[1]["new_metric_status"]="red (target not met)"
        self.notifications[0].metrics[1]["old_metric_status"]="green (target met)"

        send_notifications(self.notifications)
        mocked_send.assert_called_once()

    @patch('notification.Notification.not_ready')
    @patch('outbox.send_notification_to_teams')
    def test_deletion_of_notifications(self, mocked_send, mocked_ready):
        """Test that notifications are deleted after sending."""
        mocked_ready.side_effect = [False, False]
        for notification in self.notifications:
            notification.metrics[0]["metric_unit"]="units"
            notification.metrics[0]["new_metric_value"]=20
            notification.metrics[0]["old_metric_value"]=10
            notification.metrics[0]["new_metric_status"]="red (target not met)"
            notification.metrics[0]["old_metric_status"]="green (target met)"

            notification.metrics[1]["metric_unit"]="units"
            notification.metrics[1]["new_metric_value"]=20
            notification.metrics[1]["old_metric_value"]=10
            notification.metrics[1]["new_metric_status"]="red (target not met)"
            notification.metrics[1]["old_metric_status"]="green (target met)"

        self.assertEqual([], send_notifications(self.notifications))
