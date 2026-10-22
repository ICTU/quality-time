"""Unit tests for the Teams notification destination."""

from itertools import permutations
from typing import TYPE_CHECKING
from unittest import IsolatedAsyncioTestCase, mock

import aiohttp

from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.model.report import Report
from shared.model.subject import Subject

from destinations.ms_teams import ICONS_URL, create_message, send_notification
from models.metric_notification_data import MetricNotificationData
from models.notification import Notification

from shared_test_code.fixtures import METRIC_ID, METRIC_ID2, SUBJECT_ID

if TYPE_CHECKING:
    from shared.utils.type import MetricId

    from destinations.ms_teams import Container, Message


class MsTeamsTestCase(IsolatedAsyncioTestCase):
    """Base class for MsTeams unit tests."""

    def setUp(self):
        """Provide a default report for the rest of the class."""
        self.report_url = "https://report1"
        data_model = {}
        self.report = Report(data_model, {"title": "Report 1"})
        self.subject = Subject(data_model, {"type": "software", "name": "Subject"}, SUBJECT_ID, self.report)
        metric = self.create_metric()
        measurements = [
            Measurement(metric, {"count": {"value": "10", "status": "near_target_met"}}),
            Measurement(metric, {"count": {"value": "42", "status": "target_not_met"}}),
        ]
        self.metric_notification_data = MetricNotificationData(metric, METRIC_ID, measurements, self.subject)
        self.notification = Notification(self.report, self.report_url, [self.metric_notification_data], {})

    def create_metric(self, metric_id: MetricId = METRIC_ID, name: str | None = "Metric") -> Metric:
        """Create a metric fixture."""
        return Metric(
            {},
            {
                "type": "security_warnings",
                "name": name,
                "scale": "count",
                "unit": "security warnings",
                "unit_singular": "security warning",
            },
            metric_id,
        )


@mock.patch("logging.getLogger")
class SendNotificationToTeamsTests(MsTeamsTestCase):
    """Unit tests for the Teams destination for notifications."""

    @mock.patch("aiohttp.ClientSession.post")
    async def test_valid_webhook(self, mock_post: mock.MagicMock, mock_get_logger: mock.Mock):
        """Test that the message is posted as JSON to the webhook."""
        mock_post.return_value.__aenter__.return_value.status = 202
        await send_notification("https://webhook", self.notification)
        mock_post.assert_called_once_with("https://webhook", json=create_message(self.notification))
        mock_get_logger.return_value.debug.assert_called_once_with("Teams webhook responded with status %d", 202)
        mock_get_logger.return_value.exception.assert_not_called()

    @mock.patch("aiohttp.ClientSession.post")
    async def test_http_error(self, mock_post: mock.MagicMock, mock_get_logger: mock.Mock):
        """Test that HTTP errors are logged."""
        mock_post.side_effect = aiohttp.ClientResponseError(mock.Mock(), (), status=400)
        await send_notification("https://webhook", self.notification)
        mock_get_logger.return_value.exception.assert_called_once_with("Could not deliver notification")

    @mock.patch("aiohttp.ClientSession.post")
    async def test_connection_error(self, mock_post: mock.MagicMock, mock_get_logger: mock.Mock):
        """Test that connection errors are logged."""
        mock_post.side_effect = aiohttp.ClientConnectionError
        await send_notification("https://webhook", self.notification)
        mock_get_logger.return_value.exception.assert_called_once_with("Could not deliver notification")

    async def test_invalid_webhook(self, mock_get_logger: mock.Mock):
        """Test that invalid webhook URLs are logged."""
        await send_notification("invalid_webhook", self.notification)
        mock_get_logger.return_value.exception.assert_called_once_with("Could not deliver notification")


class BuildNotificationMessageTests(MsTeamsTestCase):
    """Unit tests for the message builder."""

    def create_container(
        self,
        title: str,
        status: str,
        status_text: str,
        value: str,
        metric_uuid: str,
    ) -> Container:
        """Create the expected Adaptive Card container for a metric."""
        return {
            "type": "Container",
            "separator": True,
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [{"type": "Image", "url": f"{ICONS_URL}/{status}.png", "size": "Small"}],
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {"type": "TextBlock", "text": title, "weight": "Bolder", "wrap": True},
                                {
                                    "type": "TextBlock",
                                    "text": "Subject",
                                    "isSubtle": True,
                                    "spacing": "None",
                                    "wrap": True,
                                },
                            ],
                        },
                    ],
                },
                {
                    "type": "FactSet",
                    "facts": [{"title": "Status:", "value": status_text}, {"title": "Value:", "value": value}],
                },
                {
                    "type": "ActionSet",
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "View metric",
                            "url": f"https://report1#{metric_uuid}",
                        },
                    ],
                },
            ],
        }

    def create_expected_message(self, summary: str, *containers: Container) -> Message:
        """Create the expected message."""
        return {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "msteams": {"width": "Full"},
                        "summary": summary,
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Quality-time notifications for Report 1",
                                "size": "Large",
                                "weight": "Bolder",
                                "wrap": True,
                            },
                            {"type": "TextBlock", "text": summary, "isSubtle": True, "wrap": True},
                            *containers,
                        ],
                    },
                },
            ],
        }

    def test_changed_status_text(self):
        """Test that the text is correct and that metrics are sorted by name."""
        metric2 = self.create_metric(METRIC_ID, name=None)
        measurements2 = [
            Measurement(metric2, {"count": {"value": "1", "status": "target_met"}}),
            Measurement(metric2, {"count": {"value": "10", "status": "target_not_met"}}),
        ]
        metric_notification_data2 = MetricNotificationData(metric2, METRIC_ID2, measurements2, self.subject)
        expected_message = self.create_expected_message(
            "Report 1 has 2 metrics that changed status",
            self.create_container(
                "Metric",
                "target_not_met",
                "target not met (red), was near target met (yellow)",
                "42 security warnings, was 10 security warnings",
                METRIC_ID,
            ),
            self.create_container(
                "Security warnings",
                "target_not_met",
                "target not met (red), was target met (green)",
                "10 security warnings, was 1 security warning",
                METRIC_ID2,
            ),
        )
        for metrics in permutations([self.metric_notification_data, metric_notification_data2]):
            with self.subTest(metrics=[metric.metric_name for metric in metrics]):
                notification = Notification(self.report, self.report_url, list(metrics), {})
                self.assertEqual(expected_message, create_message(notification))

    def test_unchanged_value(self):
        """Test that the text is correct if the status changed but the value didn't, e.g. after a target change."""
        metric = self.create_metric()
        measurements = [
            Measurement(metric, {"count": {"value": "1", "status": "target_met"}}),
            Measurement(metric, {"count": {"value": "1", "status": "target_not_met"}}),
        ]
        metric_notification_data = MetricNotificationData(metric, METRIC_ID, measurements, self.subject)
        notification = Notification(self.report, self.report_url, [metric_notification_data], {})
        expected_message = self.create_expected_message(
            "Report 1 has 1 metric that changed status",
            self.create_container(
                "Metric",
                "target_not_met",
                "target not met (red), was target met (green)",
                "1 security warning (unchanged)",
                METRIC_ID,
            ),
        )
        self.assertEqual(expected_message, create_message(notification))

    def test_unknown_new_value(self):
        """Test that the text is correct if the new value is unknown."""
        metric = self.create_metric()
        measurements = [
            Measurement(metric, {"count": {"value": "0", "status": "near_target_met"}}),
            Measurement(metric, {"count": {"value": None, "status": "unknown"}}),
        ]
        metric_notification_data = MetricNotificationData(metric, METRIC_ID, measurements, self.subject)
        notification = Notification(self.report, self.report_url, [metric_notification_data], {})
        expected_message = self.create_expected_message(
            "Report 1 has 1 metric that changed status",
            self.create_container(
                "Metric",
                "unknown",
                "unknown (white), was near target met (yellow)",
                "unknown, was 0 security warnings",
                METRIC_ID,
            ),
        )
        self.assertEqual(expected_message, create_message(notification))

    def test_unknown_old_value(self):
        """Test that the text is correct if the old value is unknown."""
        metric = self.create_metric()
        measurements = [
            Measurement(metric, {"count": {"value": None, "status": "unknown"}}),
            Measurement(metric, {"count": {"value": "0", "status": "near_target_met"}}),
        ]
        metric_notification_data = MetricNotificationData(metric, METRIC_ID, measurements, self.subject)
        notification = Notification(self.report, self.report_url, [metric_notification_data], {})
        expected_message = self.create_expected_message(
            "Report 1 has 1 metric that changed status",
            self.create_container(
                "Metric",
                "near_target_met",
                "near target met (yellow), was unknown (white)",
                "0 security warnings, was unknown",
                METRIC_ID,
            ),
        )
        self.assertEqual(expected_message, create_message(notification))
