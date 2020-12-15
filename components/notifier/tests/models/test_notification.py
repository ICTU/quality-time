""""Unit tests for the notification."""

import unittest

from models.notification import Notification


class NotificationTestCase(unittest.TestCase):
    """Unit tests for the notification class."""

    def setUp(self):
        """Set variables for the other testcases."""
        destination = dict(frequency=60)
        destination_uuid = "dest_uuid"
        metrics = {}
        report = dict(title="title")
        self.notification = Notification(report, metrics, destination_uuid, destination)

    def test_ready(self):
        """Test that a notification is ready to be sent if the frequency is 0."""
        notification = self.notification
        notification.destination["frequency"] = 0
        self.assertTrue(notification.ready())

    def test_not_ready(self):
        """Test that a notification isn't ready to be sent if the frequency hasn't expired."""
        self.assertFalse(self.notification.ready())
