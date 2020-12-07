""""Unit tests for the notification strategies."""

import json
import pathlib
import unittest

from notification import Notification


class StrategiesTestCase(unittest.TestCase):
    """Unit tests for the 'amount of new red metrics per report' notification strategy."""

    def setUp(self):
        """Set variables for the other testcases."""
        destination = dict(frequency=60)
        destination_uuid = "dest_uuid"
        metrics = dict()
        report = dict(title="title")
        self.notification = Notification(report, metrics, destination_uuid, destination)

    def test_Ready(self):
        """Test that a notification is ready to be sent if the frequency is 0."""
        notification = self.notification
        notification.destination["frequency"] = 0
        self.assertTrue(notification.ready())

    def test_not_Ready(self):
        """Test that a notification isn't ready to be sent if the frequency hasn't expired."""
        self.assertFalse(self.notification.ready())
