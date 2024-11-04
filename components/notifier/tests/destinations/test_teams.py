"""Unit tests for the Teams notification destination."""

import logging
from unittest import TestCase, mock

from pymsteams import cardsection, connectorcard

from shared.model.metric import Metric

from destinations.ms_teams import ICON_URL, create_connector_card, send_notification
from models.metric_notification_data import MetricNotificationData
from models.notification import Notification

from tests.fixtures import METRIC_ID, METRIC_ID2


class MsTeamsTestCase(TestCase):
    """Base class for MsTeams unit tests."""

    def setUp(self):
        """Provide a default report for the rest of the class."""
        self.report_url = "https://report1"
        self.report = {"title": "Report 1"}
        self.subject = {"type": "software", "name": "Subject"}
        metric = Metric(
            {},
            {
                "type": "security_warnings",
                "name": "Metric",
                "unit": "sec warnings",
                "scale": "count",
            },
            METRIC_ID,
        )
        measurements = [
            {"count": {"value": 10, "status": "near_target_met"}},
            {"count": {"value": 42, "status": "target_not_met"}},
        ]
        self.metric_notification_data = MetricNotificationData(metric, METRIC_ID, measurements, self.subject)
        self.notification = Notification(self.report, self.report_url, [self.metric_notification_data], {})


@mock.patch("pymsteams.connectorcard.send")
class SendNotificationToTeamsTests(MsTeamsTestCase):
    """Unit tests for the Teams destination for notifications."""

    def test_invalid_webhook(self, mock_send: mock.Mock):
        """Test that exceptions are caught."""
        logging.disable(logging.CRITICAL)
        mock_send.side_effect = OSError("Some error")
        send_notification("invalid_webhook", self.notification)
        mock_send.assert_called()
        logging.disable(logging.NOTSET)

    def test_valid_webhook(self, mock_send: mock.Mock):
        """Test that a valid message is sent to a valid webhook."""
        send_notification("valid_webhook", self.notification)
        mock_send.assert_called()


class BuildNotificationMessageTests(MsTeamsTestCase):
    """Unit tests for the message builder."""

    def create_section(
        self,
        title: str,
        status: str,
        status_text: str,
        value: str,
        metric_uuid: str,
    ) -> cardsection:
        """Create a notification card section."""
        section = cardsection()
        section.activityTitle(title)
        section.activitySubtitle("Subject")
        section.activityImage(ICON_URL % status)
        section.addFact("Status:", status_text)
        section.addFact("Value:", value)
        section.linkButton("View metric", f"https://report1#{metric_uuid}")
        return section

    def test_changed_status_text(self):
        """Test that the text is correct."""
        metric2 = Metric(
            {},
            {
                "type": "security_warnings",
                "name": None,
                "unit": None,
                "scale": "count",
            },
            METRIC_ID2,
        )
        measurements2 = [
            {"count": {"value": 5, "status": "target_met"}},
            {"count": {"value": 10, "status": "target_not_met"}},
        ]
        metric_notification_data2 = MetricNotificationData(metric2, METRIC_ID2, measurements2, self.subject)
        notification = Notification(
            self.report, self.report_url, [self.metric_notification_data, metric_notification_data2], {}
        )
        expected_card = connectorcard("destination")
        expected_card.title("Quality-time notifications for Report 1")
        expected_card.summary("Report 1 has 2 metrics that changed status")
        expected_card.addSection(
            self.create_section(
                "Metric",
                "target_not_met",
                "target not met (red), was near target met (yellow)",
                "42 sec warnings, was 10 sec warnings",
                METRIC_ID,
            )
        )
        expected_card.addSection(
            self.create_section(
                "Security warnings",
                "target_not_met",
                "target not met (red), was target met (green)",
                "10 security warnings, was 5 security warnings",
                METRIC_ID2,
            )
        )
        self.assertEqual(expected_card.payload, create_connector_card("destination", notification).payload)

    def test_unknown_text(self):
        """Test that the text is correct."""
        metric = Metric(
            {},
            {
                "type": "metric_type",
                "name": "Metric",
                "unit": "units",
                "scale": "count",
            },
            METRIC_ID,
        )
        measurements = [
            {"count": {"value": 0, "status": "near_target_met"}},
            {"count": {"value": None, "status": "unknown"}},
        ]
        metric_notification_data = MetricNotificationData(metric, METRIC_ID, measurements, self.subject)
        notification = Notification(self.report, self.report_url, [metric_notification_data], {})
        expected_card = connectorcard("destination")
        expected_card.title("Quality-time notifications for Report 1")
        expected_card.summary("Report 1 has 1 metric that changed status")
        expected_card.addSection(
            self.create_section(
                "Metric",
                "unknown",
                "unknown (white), was near target met (yellow)",
                "unknown, was 0 units",
                METRIC_ID,
            )
        )
        self.assertEqual(expected_card.payload, create_connector_card("destination", notification).payload)
