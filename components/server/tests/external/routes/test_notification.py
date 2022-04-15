"""Unit tests for the notification routes."""

import unittest
from unittest.mock import Mock, patch

from shared.model.report import Report

from external.routes import (
    post_new_notification_destination,
    delete_notification_destination,
    post_notification_destination_attributes,
)

from ...fixtures import REPORT_ID, NOTIFICATION_DESTINATION_ID, create_report


class NotificationTestCase(unittest.TestCase):  # skipcq: PTC-W0046
    """Base class for notification unit tests."""

    def setUp(self):
        """Set up the database."""
        self.database = Mock()
        self.report = Report({}, create_report())
        self.database.reports.find_one.return_value = self.report
        self.database.datamodels.find_one.return_value = dict(_id="id")
        self.email = "jenny@example.org"
        self.database.sessions.find_one.return_value = dict(user="Jenny", email=self.email)

    def assert_delta(self, description, uuids=None, report=None):
        """Check that the delta description is correct."""
        report = report if report is not None else self.report
        uuids = sorted(uuids or [REPORT_ID, NOTIFICATION_DESTINATION_ID])
        self.assertEqual(dict(uuids=uuids, email=self.email, description=description), report["delta"])


@patch("bottle.request")
class PostNotificationAttributesTest(NotificationTestCase):
    """Unit tests for the post notification destination attributes route."""

    def test_post_notification_destination_attribute(self, request):
        """Test changing the name of a notification destination."""
        request.json = dict(name="new name")
        post_notification_destination_attributes(REPORT_ID, NOTIFICATION_DESTINATION_ID, self.database)
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            description="Jenny changed the 'name' of notification destination 'notification_destination' "
            "in report 'Report' from 'notification_destination' to 'new name'.",
            report=updated_report,
        )

    def test_post_notification_destination_unchanged_attribute(self, request):
        """Test changing the name of a notification destination."""
        request.json = dict(name="notification_destination")
        post_notification_destination_attributes(REPORT_ID, NOTIFICATION_DESTINATION_ID, self.database)
        self.database.reports.insert_one.assert_not_called()

    def test_post_multiple_notification_destination_attributes(self, request):
        """Test changing the name and url of a notification destination."""
        request.json = dict(name="new name", url="https://newurl")
        post_notification_destination_attributes(REPORT_ID, NOTIFICATION_DESTINATION_ID, self.database)
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            description="Jenny changed the 'name' and 'url' of notification destination 'notification_destination' "
            "in report 'Report' from 'notification_destination' and 'https://reporturl' to 'new name' and "
            "'https://newurl'.",
            report=updated_report,
        )


class NotificationDestinationTest(NotificationTestCase):
    """Unit tests for adding and deleting notification destinations."""

    def test_add_new_notification_destination(self):
        """Test that a notification destination can be added."""
        self.assertTrue(post_new_notification_destination(REPORT_ID, self.database)["ok"])
        notification_destinations_uuid = list(self.report["notification_destinations"].keys())[1]
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            description="Jenny created a new destination for notifications in report 'Report'.",
            uuids=[REPORT_ID, notification_destinations_uuid],
            report=updated_report,
        )

    def test_add_first_new_notification_destination(self):
        """Test that a notification destination can be added."""
        del self.report["notification_destinations"]
        self.assertTrue(post_new_notification_destination(REPORT_ID, self.database)["ok"])
        updated_report = self.database.reports.insert_one.call_args[0][0]
        notification_destinations_uuid = list(updated_report["notification_destinations"].keys())[0]
        self.assert_delta(
            description="Jenny created a new destination for notifications in report 'Report'.",
            uuids=[REPORT_ID, notification_destinations_uuid],
            report=updated_report,
        )

    def test_delete_notification_destination(self):
        """Test that a notification destination can be deleted."""
        self.assertEqual(
            dict(ok=True), delete_notification_destination(REPORT_ID, NOTIFICATION_DESTINATION_ID, self.database)
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            description="Jenny deleted destination notification_destination from report 'Report'.",
            uuids=[REPORT_ID, NOTIFICATION_DESTINATION_ID],
            report=updated_report,
        )
