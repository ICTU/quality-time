"""Unit tests for the Teams notification destination."""

import logging
from unittest import mock, TestCase

from destinations.ms_teams import build_notification_text, send_notification_to_teams


@mock.patch('pymsteams.connectorcard.send')
class SendNotificationToTeamsTests(TestCase):
    """Unit tests for the Teams destination for notifications."""

    def setUp(self):
        """Provide the text contents to the rest of the class."""
        self.message = "notification message"

    def test_invalid_webhook(self, mock_send):
        """Test that exceptions are caught."""
        logging.disable(logging.CRITICAL)  # Don't log to stderr during this unit test
        mock_send.side_effect = OSError("Some error")
        send_notification_to_teams("invalid_webhook", self.message)
        mock_send.assert_called()
        logging.disable(logging.NOTSET)  # Reset the logging

    def test_valid_webhook(self, mock_send):
        """Test that a valid message is sent to a valid webhook."""
        send_notification_to_teams("valid_webhook", self.message)
        mock_send.assert_called()


class BuildNotificationTextTests(TestCase):
    """Unit tests for the message builder."""

    def test_text(self):
        """Test that the text is correct."""
        text = build_notification_text(
            dict(
                report_uuid="report1", report_title="Report 1", url="https://report1",
                metrics=[
                    dict(
                        metric_type="metric_type",
                        metric_name="Metric",
                        metric_unit="units",
                        old_metric_status="yellow (near target met)",
                        old_metric_value=0,
                        new_metric_status="red (target not met)",
                        new_metric_value=42),
                    dict(
                        metric_type="metric_type",
                        metric_name="Metric",
                        metric_unit="units",
                        old_metric_status="green (target met)",
                        old_metric_value=5,
                        new_metric_status="red (target not met)",
                        new_metric_value=10)]))
        self.assertEqual(
            "[Report 1](https://report1) has 2 metrics that changed status:\n\n"
            "* Metric status is red (target not met), was yellow (near target met). Value is 42 units, was 0 units.\n"
            "* Metric status is red (target not met), was green (target met). Value is 10 units, was 5 units.\n",
            text)

    def test_unknown_text(self):
        """Test that the text is correct."""
        text = build_notification_text(
            dict(
                report_uuid="report1", report_title="Report 1", url="https://report1",
                metrics=[
                    dict(
                        metric_type="metric_type",
                        metric_name="Metric",
                        metric_unit="units",
                        old_metric_status="yellow (near target met)",
                        old_metric_value=0,
                        new_metric_status="white (unknown)",
                        new_metric_value=None)]))
        self.assertEqual(
            "[Report 1](https://report1) has 1 metric that changed status:\n\n"
            "* Metric status is white (unknown), was yellow (near target met). Value is ? units, was 0 units.\n",
            text)
