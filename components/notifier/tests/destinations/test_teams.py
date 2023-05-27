"""Unit tests for the Teams notification destination."""

import logging
from unittest import TestCase, mock

from destinations.ms_teams import notification_text, send_notification
from models.metric_notification_data import MetricNotificationData
from models.notification import Notification


@mock.patch("pymsteams.connectorcard.send")
class SendNotificationToTeamsTests(TestCase):
    """Unit tests for the Teams destination for notifications."""

    def setUp(self):
        """Provide the text contents to the rest of the class."""
        self.message = "notification message"

    def test_invalid_webhook(self, mock_send: mock.Mock):
        """Test that exceptions are caught."""
        logging.disable(logging.CRITICAL)
        mock_send.side_effect = OSError("Some error")
        send_notification("invalid_webhook", self.message)
        mock_send.assert_called()
        logging.disable(logging.NOTSET)

    def test_valid_webhook(self, mock_send: mock.Mock):
        """Test that a valid message is sent to a valid webhook."""
        send_notification("valid_webhook", self.message)
        mock_send.assert_called()


class BuildNotificationTextTests(TestCase):
    """Unit tests for the message builder."""

    def setUp(self):
        """Provide a default report for the rest of the class."""
        self.report = {"title": "Report 1", "url": "https://report1"}
        self.subject = {"type": "software", "name": "Subject"}

    def test_changed_status_text(self):
        """Test that the text is correct."""
        scale = "count"
        metric1 = {
            "type": "security_warnings",
            "name": "Metric",
            "unit": "my security warnings",
            "scale": scale,
        }
        measurements1 = [
            {"count": {"value": 0, "status": "near_target_met"}},
            {"count": {"value": 42, "status": "target_not_met"}},
        ]
        metric2 = {
            "type": "security_warnings",
            "name": None,
            "unit": None,
            "scale": scale,
        }
        measurements2 = [
            {"count": {"value": 5, "status": "target_met"}},
            {"count": {"value": 10, "status": "target_not_met"}},
        ]
        metric_notification_data1 = MetricNotificationData(metric1, measurements1, self.subject)
        metric_notification_data2 = MetricNotificationData(metric2, measurements2, self.subject)
        notification = Notification(
            self.report,
            [metric_notification_data1, metric_notification_data2],
            "destination_uuid",
            {},
        )
        self.assertEqual(
            "[Report 1](https://report1) has 2 metrics that changed status:\n\n"
            "* Subject:\n"
            "  * *Metric* status is red (target not met), was yellow (near target met). "
            "Value is 42 my security warnings, was 0 my security warnings.\n"
            "  * *Security warnings* status is red (target not met), was green (target met). "
            "Value is 10 security warnings, was 5 security warnings.\n",
            notification_text(notification),
        )

    def test_unknown_text(self):
        """Test that the text is correct."""
        metric1 = {
            "type": "metric_type",
            "name": "Metric",
            "unit": "units",
            "scale": "count",
        }
        measurements = [
            {"count": {"value": 0, "status": "near_target_met"}},
            {"count": {"value": None, "status": "unknown"}},
        ]
        metric_notification_data1 = MetricNotificationData(metric1, measurements, self.subject)
        notification = Notification(self.report, [metric_notification_data1], "destination_uuid", {})
        self.assertEqual(
            "[Report 1](https://report1) has 1 metric that changed status:\n\n"
            "* Subject:\n"
            "  * *Metric* status is white (unknown), was yellow (near target met). "
            "Value is ? units, was 0 units.\n",
            notification_text(notification),
        )
