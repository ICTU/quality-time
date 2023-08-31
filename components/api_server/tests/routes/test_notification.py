"""Unit tests for the notification routes."""

from unittest.mock import patch

from shared.model.report import Report
from shared.utils.functions import first

from routes import (
    post_new_notification_destination,
    delete_notification_destination,
    post_notification_destination_attributes,
)

from tests.base import DataModelTestCase
from tests.fixtures import REPORT_ID, NOTIFICATION_DESTINATION_ID, create_report


class NotificationTestCase(DataModelTestCase):
    """Base class for notification unit tests."""

    def setUp(self):
        """Extend to set up the database."""
        super().setUp()
        self.report = Report(self.DATA_MODEL, create_report())
        self.database.reports.find_one.return_value = self.report
        self.email = "jenny@example.org"
        self.database.sessions.find_one.return_value = {"user": "Jenny", "email": self.email}

    def assert_delta(self, description, uuids=None, report=None):
        """Check that the delta description is correct."""
        report = report if report is not None else self.report
        uuids = sorted(uuids or [REPORT_ID, NOTIFICATION_DESTINATION_ID])
        self.assertEqual({"uuids": uuids, "email": self.email, "description": description}, report["delta"])


@patch("bottle.request")
class PostNotificationAttributesTest(NotificationTestCase):
    """Unit tests for the post notification destination attributes route."""

    new_name = "New name"
    new_url = "https://newurl"

    def test_post_notification_destination_attribute(self, request):
        """Test changing the name of a notification destination."""
        request.json = {"name": self.new_name}
        post_notification_destination_attributes(self.database, REPORT_ID, NOTIFICATION_DESTINATION_ID)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual(
            self.new_name,
            updated_report["notification_destinations"][NOTIFICATION_DESTINATION_ID]["name"],
        )
        self.assert_delta(
            description="Jenny changed the 'name' of notification destination 'notification_destination' "
            f"in report 'Report' from 'notification_destination' to '{self.new_name}'.",
            report=updated_report,
        )

    def test_post_notification_destination_unchanged_attribute(self, request):
        """Test changing the name of a notification destination."""
        request.json = {"name": "notification_destination"}
        post_notification_destination_attributes(self.database, REPORT_ID, NOTIFICATION_DESTINATION_ID)
        self.database.reports.insert_one.assert_not_called()

    def test_post_multiple_notification_destination_attributes(self, request):
        """Test changing the name and url of a notification destination."""
        request.json = {"name": self.new_name, "url": self.new_url}
        post_notification_destination_attributes(self.database, REPORT_ID, NOTIFICATION_DESTINATION_ID)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        updated_notification_destination = updated_report["notification_destinations"][NOTIFICATION_DESTINATION_ID]
        self.assertEqual(self.new_name, updated_notification_destination["name"])
        self.assertEqual(self.new_url, updated_notification_destination["url"])
        self.assert_delta(
            description="Jenny changed the 'name' and 'url' of notification destination 'notification_destination' "
            f"in report 'Report' from 'notification_destination' and 'https://reporturl' to '{self.new_name}' and "
            f"'{self.new_url}'.",
            report=updated_report,
        )

    def test_non_existing_report(self, request):
        """Test that an error is returned if the report is missing."""
        request.json = {"name": self.new_name}
        self.database.reports.find_one.return_value = None
        self.assertEqual(
            {"ok": False, "error": f"Report with UUID {REPORT_ID} not found."},
            post_notification_destination_attributes(self.database, REPORT_ID, NOTIFICATION_DESTINATION_ID),
        )


class NotificationDestinationTest(NotificationTestCase):
    """Unit tests for adding and deleting notification destinations."""

    def test_add_new_notification_destination(self):
        """Test that a notification destination can be added."""
        self.assertTrue(post_new_notification_destination(self.database, REPORT_ID)["ok"])
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
        self.assertTrue(post_new_notification_destination(self.database, REPORT_ID)["ok"])
        updated_report = self.database.reports.insert_one.call_args[0][0]
        notification_destinations_uuid = first(updated_report["notification_destinations"].keys())
        self.assert_delta(
            description="Jenny created a new destination for notifications in report 'Report'.",
            uuids=[REPORT_ID, notification_destinations_uuid],
            report=updated_report,
        )

    def test_delete_notification_destination(self):
        """Test that a notification destination can be deleted."""
        self.assertEqual(
            {"ok": True},
            delete_notification_destination(self.database, REPORT_ID, NOTIFICATION_DESTINATION_ID),
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            description="Jenny deleted destination notification_destination from report 'Report'.",
            uuids=[REPORT_ID, NOTIFICATION_DESTINATION_ID],
            report=updated_report,
        )

    def test_non_existing_report(self):
        """Test that an error is returned if the report is missing."""
        self.database.reports.find_one.return_value = None
        error_message = {"ok": False, "error": f"Report with UUID {REPORT_ID} not found."}
        self.assertEqual(error_message, post_new_notification_destination(self.database, REPORT_ID))
        self.assertEqual(
            error_message,
            delete_notification_destination(self.database, REPORT_ID, NOTIFICATION_DESTINATION_ID),
        )
