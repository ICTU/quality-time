"""Unit tests for the Teams notification destination."""

from unittest import mock, TestCase
from quality_time_notifier import send_notification_to_teams


class TeamsTestCase(TestCase):
    """Unit tests for the Teams destination for notifications."""
    def test_invalid_webhook(self):
        result = send_notification_to_teams("notavaliddestination", "message")
        expected_result = False
        self.assertEqual(result, expected_result)

    def test_no_destination_configured(self):
        result = send_notification_to_teams(None, "message")
        expected_result = False
        self.assertEqual(result, expected_result)

    @mock.patch('quality_time_notifier.send_notification_to_teams', return_value=True)
    def test_valid_webhook(self, mock_teams_destination):
        result = send_notification_to_teams("", "test")
        expected_result = True
        self.assertEqual(result, expected_result)
