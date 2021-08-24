"""Unit tests for the Teams notification destination."""

import logging
from unittest import mock, TestCase

from destinations.ms_teams import build_notification_text, send_notification
from models.notification import Notification
from models.metric_notification_data import MetricNotificationData

from ..data_model import DATA_MODEL


@mock.patch("pymsteams.connectorcard.send")
class SendNotificationToTeamsTests(TestCase):
    """Unit tests for the Teams destination for notifications."""

    def setUp(self):
        """Provide the text contents to the rest of the class."""
        self.message = "notification message"

    def test_invalid_webhook(self, mock_send):
        """Test that exceptions are caught."""
        logging.disable(logging.CRITICAL)  # Don't log to stderr during this unit test
        mock_send.side_effect = OSError("Some error")
        send_notification("invalid_webhook", self.message)
        mock_send.assert_called()
        logging.disable(logging.NOTSET)  # Reset the logging

    def test_valid_webhook(self, mock_send):
        """Test that a valid message is sent to a valid webhook."""
        send_notification("valid_webhook", self.message)
        mock_send.assert_called()


class BuildNotificationTextTests(TestCase):
    """Unit tests for the message builder."""

    def setUp(self):
        """Provide a default report for the rest of the class."""
        self.report = dict(title="Report 1", url="https://report1")
        self.subject = dict(type="software", name="Subject")

    def test_changed_status_text(self):
        """Test that the text is correct."""
        scale = "count"
        metric1 = dict(
            type="metric_type",
            name="Metric",
            unit="units",
            scale=scale,
            recent_measurements=[
                dict(count=dict(value=0, status="near_target_met")),
                dict(count=dict(value=42, status="target_not_met")),
            ],
        )
        metric2 = dict(
            type="metric_type",
            name="Metric",
            unit="units",
            scale=scale,
            recent_measurements=[
                dict(count=dict(value=5, status="target_met")),
                dict(count=dict(value=10, status="target_not_met")),
            ],
        )
        metric_notification_data1 = MetricNotificationData(metric1, self.subject, DATA_MODEL)
        metric_notification_data2 = MetricNotificationData(metric2, self.subject, DATA_MODEL)
        notification = Notification(
            self.report, [metric_notification_data1, metric_notification_data2], "destination_uuid", {}
        )
        text = build_notification_text(notification)
        self.assertEqual(
            "[Report 1](https://report1) has 2 metrics that changed status:\n\n"
            "* Subject:\n"
            "  * *Metric* status is red (target not met), was yellow (near target met). "
            "Value is 42 units, was 0 units.\n"
            "  * *Metric* status is red (target not met), was green (target met). "
            "Value is 10 units, was 5 units.\n",
            text,
        )

    def test_unknown_text(self):
        """Test that the text is correct."""
        metric1 = dict(
            type="metric_type",
            name="Metric",
            unit="units",
            scale="count",
            recent_measurements=[
                dict(count=dict(value=0, status="near_target_met")),
                dict(count=dict(value=None, status="unknown")),
            ],
        )
        metric_notification_data1 = MetricNotificationData(metric1, self.subject, DATA_MODEL)
        notification = Notification(self.report, [metric_notification_data1], "destination_uuid", {})
        text = build_notification_text(notification)
        self.assertEqual(
            "[Report 1](https://report1) has 1 metric that changed status:\n\n"
            "* Subject:\n"
            "  * *Metric* status is white (unknown), was yellow (near target met). "
            "Value is ? units, was 0 units.\n",
            text,
        )
