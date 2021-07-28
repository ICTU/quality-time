"""Unit tests for the Teams notification destination."""

import logging
from unittest import mock, TestCase

from destinations.ms_teams import build_notification_text, send_notification
from models.notification import Notification
from models.metric_notification_data import MetricNotificationData


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
        self.data_model = dict(
            metrics=dict(metric_type=dict(name="type")),
            sources=dict(
                quality_time=dict(
                    parameters=dict(
                        status=dict(
                            api_values={
                                "target met (green)": "target_met",
                                "near target met (yellow)": "near_target_met",
                                "target not met (red)": "target_not_met",
                                "technical debt target met (grey)": "debt_target_met",
                                "unknown (white)": "unknown",
                            }
                        )
                    )
                )
            ),
        )
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
        metric_notification_data1 = MetricNotificationData(metric1, self.subject, self.data_model, "status_changed")
        metric_notification_data2 = MetricNotificationData(metric2, self.subject, self.data_model, "status_changed")
        notification = Notification(
            self.report, [metric_notification_data1, metric_notification_data2], "destination_uuid", {}
        )
        text = build_notification_text(notification)
        self.assertEqual(
            "[Report 1](https://report1) has 2 metrics that are notable:\n\n"
            "* Metric status is red (target not met), was yellow (near target met). Value is 42 units, was 0 units.\n"
            "* Metric status is red (target not met), was green (target met). Value is 10 units, was 5 units.\n",
            text,
        )

    def test_unchanged_status_text(self):
        """Test that the text is correct."""
        scale = "count"
        metric1 = dict(
            type="metric_type",
            name="Metric",
            unit="units",
            scale=scale,
            recent_measurements=[
                dict(count=dict(value=0, status="near_target_met")),
                dict(count=dict(value=42, status="near_target_met")),
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
        metric_notification_data1 = MetricNotificationData(
            metric1, self.subject, self.data_model, "status_long_unchanged"
        )
        metric_notification_data2 = MetricNotificationData(
            metric2, self.subject, self.data_model, "status_long_unchanged"
        )
        notification = Notification(
            self.report, [metric_notification_data1, metric_notification_data2], "destination_uuid", {}
        )
        text = build_notification_text(notification)
        self.assertEqual(
            "[Report 1](https://report1) has 2 metrics that are notable:\n\n"
            "* Metric has been yellow (near target met) for three weeks. Value: 42 units.\n"
            "* Metric has been red (target not met) for three weeks. Value: 10 units.\n",
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
        metric_notification_data1 = MetricNotificationData(metric1, self.subject, self.data_model, "status_changed")
        notification = Notification(self.report, [metric_notification_data1], "destination_uuid", {})
        text = build_notification_text(notification)
        self.assertEqual(
            "[Report 1](https://report1) has 1 metric that is notable:\n\n"
            "* Metric status is white (unknown), was yellow (near target met). Value is ? units, was 0 units.\n",
            text,
        )
