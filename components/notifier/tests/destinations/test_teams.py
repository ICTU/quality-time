"""Unit tests for the Teams notification destination."""

import logging
from unittest import mock, TestCase

from destinations.ms_teams import build_notification_text, SALUTATIONS, send_notification_to_teams


@mock.patch('pymsteams.connectorcard.send')
class SendNotificationToTeamsTests(TestCase):
    """Unit tests for the Teams destination for notifications."""

    def setUp(self):
        self.message = "notification message"

    def test_invalid_webhook(self, mock_send):
        """Test that exceptions are caught."""
        logging.disable(logging.CRITICAL)  # Don't log to stderr during this unit test
        mock_send.side_effect = OSError("Some error")
        send_notification_to_teams("invalid_webhook", self.message)
        mock_send.assert_called()
        logging.disable(logging.NOTSET)  # Reset the logging

    def test_valid_webhook(self, mock_send):
        """test that a valid message is sent to a valid webhook."""
        send_notification_to_teams("valid_webhook", self.message)
        mock_send.assert_called()


class BuildNotificationTextTests(TestCase):
    """Unit tests for the message builder."""

    def test_text(self):
        """Test that the text is correct."""
        text = build_notification_text(
            dict(report_uuid="report1", report_title="Report 1", new_red_metrics=2, url="http://report1"))
        salutation, contents = text.split(", ")
        self.assertEqual("[Report 1](http://report1) has 2 metrics that turned red.", contents)
        self.assertIn(salutation, SALUTATIONS)
