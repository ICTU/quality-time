"""Unit tests for the notification routes."""

import unittest
from unittest.mock import Mock, patch

from routes.external import (
    post_new_notification_destination,
    delete_notification_destination,
    post_notification_destination_attributes,
)

from ...fixtures import REPORT_ID, NOTIFICATION_DESTINATION_ID, create_report


@patch("bottle.request")
class PostNotificationAttributesTest(unittest.TestCase):
    """Unit tests for the post notification destination attributes route."""

    def setUp(self):
        """Define variables that are used in multiple tests."""
        self.database = Mock()
        self.report = dict(
            _id="id",
            report_uuid=REPORT_ID,
            title="Report",
            notification_destinations={
                NOTIFICATION_DESTINATION_ID: dict(teams_webhook="", name="notification_destination", url="")
            },
        )
        self.database.reports.find.return_value = [self.report]
        self.database.datamodels.find_one.return_value = dict(_id="id")
        self.email = "john@example.org"
        self.database.sessions.find_one.return_value = dict(user="John", email=self.email)

    def test_post_notification_destination_attribute(self, request):
        """Test changing the name of a notification destination."""
        request.json = dict(name="new name")
        post_notification_destination_attributes(REPORT_ID, NOTIFICATION_DESTINATION_ID, self.database)
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(
                uuids=[REPORT_ID, NOTIFICATION_DESTINATION_ID],
                email=self.email,
                description="John changed the 'name' of notification destination 'notification_destination' "
                "in report 'Report' from 'notification_destination' to 'new name'.",
            ),
            self.report["delta"],
        )

    def test_post_notification_destination_unchanged_attribute(self, request):
        """Test changing the name of a notification destination."""
        request.json = dict(name="notification_destination")
        post_notification_destination_attributes(REPORT_ID, NOTIFICATION_DESTINATION_ID, self.database)
        self.database.reports.insert.assert_not_called()

    def test_post_multiple_notification_destination_attributes(self, request):
        """Test changing the name and url of a notification destination."""
        request.json = dict(name="new name", url="https://newurl")
        post_notification_destination_attributes(REPORT_ID, NOTIFICATION_DESTINATION_ID, self.database)
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(
                uuids=[REPORT_ID, NOTIFICATION_DESTINATION_ID],
                email=self.email,
                description="John changed the 'name' and 'url' of notification destination 'notification_destination' "
                "in report 'Report' from 'notification_destination' and '' to 'new name' and "
                "'https://newurl'.",
            ),
            self.report["delta"],
        )


class NotificationDestinationTest(unittest.TestCase):
    """Unit tests for adding and deleting notification destinations."""

    def setUp(self):
        """Define variables that are used in multiple tests."""
        self.report = create_report()
        self.database = Mock()
        self.database.reports.find.return_value = [self.report]
        self.database.datamodels.find_one.return_value = dict(_id="id")
        self.email = "jenny@example.org"
        self.database.sessions.find_one.return_value = dict(user="Jenny", email=self.email)

    def test_add_new_notification_destination(self):
        """Test that a notification destination can be added."""
        self.assertTrue(post_new_notification_destination(REPORT_ID, self.database)["ok"])
        notification_destinations_uuid = list(self.report["notification_destinations"].keys())[1]
        self.assertEqual(
            dict(
                uuids=[REPORT_ID, notification_destinations_uuid],
                email=self.email,
                description="Jenny created a new destination for notifications in report 'Report'.",
            ),
            self.report["delta"],
        )

    def test_add_first_new_notification_destination(self):
        """Test that a notification destination can be added."""
        report_without_destinations = self.report
        del report_without_destinations["notification_destinations"]
        self.database.reports.find.return_value = [report_without_destinations]

        self.assertTrue(post_new_notification_destination(REPORT_ID, self.database)["ok"])
        notification_destinations_uuid = list(report_without_destinations["notification_destinations"].keys())[0]
        self.assertEqual(
            dict(
                uuids=[REPORT_ID, notification_destinations_uuid],
                email=self.email,
                description="Jenny created a new destination for notifications in report 'Report'.",
            ),
            report_without_destinations["delta"],
        )

    def test_delete_notification_destination(self):
        """Test that a notification destination can be deleted."""
        self.assertEqual(
            dict(ok=True), delete_notification_destination(REPORT_ID, NOTIFICATION_DESTINATION_ID, self.database)
        )
        self.assertEqual(
            dict(
                uuids=[REPORT_ID, NOTIFICATION_DESTINATION_ID],
                email=self.email,
                description="Jenny deleted destination notification_destination from report 'Report'.",
            ),
            self.report["delta"],
        )
