"""Unit tests for the Teams notification destination."""

from unittest import mock, TestCase

from destinations.ms_teams import send_notification_to_teams


@mock.patch('pymsteams.connectorcard.send')
class TeamsTestCase(TestCase):
    """Unit tests for the Teams destination for notifications."""

    def test_invalid_webhook(self, mock_send):
        """Test that exceptions are caught."""
        mock_send.side_effect = OSError
        self.assertFalse(send_notification_to_teams("invalid_webhook", "message"))

    def test_no_destination_configured(self, mock_send):
        """Test that a valid message is not sent if there is no webhook."""
        self.assertFalse(send_notification_to_teams(None, "message"))
        mock_send.assert_not_called()

    def test_valid_webhook(self, mock_send):
        """test that a valid message is sent to a valid webhook."""
        self.assertTrue(send_notification_to_teams("valid_webhook", "message"))
        mock_send.assert_called()

    def test_invalid_message(self, mock_send):
        """Test that an empty message is not sent."""
        self.assertFalse(send_notification_to_teams("valid_webhook", ""))
        mock_send.assert_not_called()
