"""Unit tests for the source location routes."""

from unittest.mock import Mock, patch

import requests

from model.transformations import CREDENTIALS_REPLACEMENT_TEXT

from routes import (
    delete_source_location,
    get_source_location,
    post_source_location_attribute,
    post_source_location_new,
    post_source_location_parameter,
)

from tests.base import DataModelTestCase
from tests.fixtures import (
    METRIC_ID,
    REPORT_ID,
    SOURCE_ID,
    SOURCE_LOCATION_ID,
    SUBJECT_ID,
    create_report,
    create_source_location,
)

UNKNOWN_UUID = "unknown_uuid"


class SourceLocationTestCase(DataModelTestCase):
    """Common fixtures for the source location route unit tests."""

    def setUp(self):
        """Extend to set up the report fixture and a user session."""
        super().setUp()
        self.email = "jenny@example.org"
        self.database.sessions.find_one.return_value = {"user": "Jenny", "email": self.email}
        self.database.measurements.find.return_value = []
        self.report = create_report()
        self.database.reports.find.return_value = [self.report]
        self.database.reports.find_one.return_value = self.report

    def assert_delta(self, description: str, uuids, report) -> None:
        """Check that the report has the correct delta."""
        self.assertEqual(
            {"uuids": sorted(uuids), "email": self.email, "description": f"Jenny {description}"},
            report["delta"],
        )

    def assert_missing_source_location(self, response) -> None:
        """Check that the response is a source-location-not-found error message."""
        self.assertEqual(
            {"ok": False, "error": f"Source location with UUID {UNKNOWN_UUID} not found."},
            response,
        )


@patch("bottle.request")
class PostSourceLocationNewTest(SourceLocationTestCase):
    """Unit tests for the post new source location route."""

    def test_new_source_location(self, request):
        """Test that a new source location can be added to a report."""
        request.json = {"type": "sonarqube"}
        response = post_source_location_new(self.database, REPORT_ID)
        self.assertTrue(response["ok"])
        new_source_location_uuid = response["new_source_location_uuid"]
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual(
            {
                "location_name": "",
                "source_type": "sonarqube",
                "url": "",
                "landing_url": "",
                "username": "",
                "password": "",  # nosec
                "private_token": "",  # nosec
            },
            updated_report["source_locations"][new_source_location_uuid],
        )
        self.assert_delta(
            "added a new source location of type 'SonarQube' to report 'Report'.",
            [REPORT_ID, new_source_location_uuid],
            updated_report,
        )

    def test_new_source_location_for_type_without_locations(self, request):
        """Test that source types without location parameters cannot get a source location."""
        request.json = {"type": "calendar"}
        self.assertEqual(
            {"ok": False, "error": "Source type 'calendar' does not have source locations."},
            post_source_location_new(self.database, REPORT_ID),
        )
        self.database.reports.insert_one.assert_not_called()

    def test_new_source_location_for_unknown_type(self, request):
        """Test that unknown source types cannot get a source location."""
        request.json = {"type": "unknown_source_type"}
        self.assertEqual(
            {"ok": False, "error": "Source type 'unknown_source_type' does not have source locations."},
            post_source_location_new(self.database, REPORT_ID),
        )
        self.database.reports.insert_one.assert_not_called()


class GetSourceLocationTest(SourceLocationTestCase):
    """Unit tests for the get source location route."""

    def test_get_source_location(self):
        """Test that the source location is returned with the credentials hidden."""
        response = get_source_location(SOURCE_LOCATION_ID, self.database)
        self.assertTrue(response["ok"])
        self.assertEqual(SOURCE_LOCATION_ID, response["source_location_uuid"])
        self.assertEqual(
            create_source_location(password=CREDENTIALS_REPLACEMENT_TEXT),
            response["source_location"],
        )

    def test_get_source_location_does_not_mask_empty_credentials(self):
        """Test that empty credentials are not masked."""
        self.report["source_locations"][SOURCE_LOCATION_ID]["password"] = ""  # nosec
        response = get_source_location(SOURCE_LOCATION_ID, self.database)
        self.assertEqual("", response["source_location"]["password"])

    def test_get_missing_source_location(self):
        """Test that a missing source location results in an error message."""
        self.assert_missing_source_location(get_source_location(UNKNOWN_UUID, self.database))


@patch("bottle.request")
class PostSourceLocationAttributeTest(SourceLocationTestCase):
    """Unit tests for the post source location attribute route."""

    def test_change_location_name(self, request):
        """Test that the source location name can be changed."""
        request.json = {"location_name": "New location name"}
        response = post_source_location_attribute(SOURCE_LOCATION_ID, "location_name", self.database)
        self.assertEqual({"ok": True}, response)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual(
            "New location name",
            updated_report["source_locations"][SOURCE_LOCATION_ID]["location_name"],
        )
        self.assert_delta(
            "changed the location_name of source location 'Source location' in report 'Report' "
            "from 'Source location' to 'New location name'.",
            [REPORT_ID, SOURCE_LOCATION_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            updated_report,
        )

    def test_no_change(self, request):
        """Test that no new report is inserted when the attribute is unchanged."""
        request.json = {"location_name": "Source location"}
        response = post_source_location_attribute(SOURCE_LOCATION_ID, "location_name", self.database)
        self.assertEqual({"ok": True}, response)
        self.database.reports.insert_one.assert_not_called()

    def test_change_attribute_of_missing_source_location(self, request):
        """Test that changing an attribute of a missing source location results in an error message."""
        request.json = {"location_name": "New location name"}
        self.assert_missing_source_location(
            post_source_location_attribute(UNKNOWN_UUID, "location_name", self.database),
        )
        self.database.reports.insert_one.assert_not_called()

    def test_source_type_name_is_used_when_location_has_no_name(self, request):
        """Test that the source type name is used in the delta description when the location has no name."""
        self.report["source_locations"][SOURCE_LOCATION_ID]["location_name"] = ""
        request.json = {"location_name": "New location name"}
        post_source_location_attribute(SOURCE_LOCATION_ID, "location_name", self.database)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "changed the location_name of source location 'SonarQube' in report 'Report' "
            "from '' to 'New location name'.",
            [REPORT_ID, SOURCE_LOCATION_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            updated_report,
        )


@patch("bottle.request")
class PostSourceLocationParameterTest(SourceLocationTestCase):
    """Unit tests for the post source location parameter route."""

    def test_change_url(self, request):
        """Test that the url can be changed and that the availability is checked."""
        request.json = {"url": "https://new-url"}
        with patch.object(requests, "get", return_value=Mock(status_code=200, reason="OK")):
            response = post_source_location_parameter(SOURCE_LOCATION_ID, "url", self.database)
        self.assertTrue(response["ok"])
        self.assertEqual(
            {
                "status_code": 200,
                "reason": "OK",
                "parameter_key": "url",
                "source_uuid": SOURCE_LOCATION_ID,
            },
            response["availability"],
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual("https://new-url", updated_report["source_locations"][SOURCE_LOCATION_ID]["url"])
        self.assert_delta(
            "changed the url of source location 'Source location' in report 'Report' "
            "from 'https://url' to 'https://new-url'.",
            [REPORT_ID, SOURCE_LOCATION_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            updated_report,
        )

    def test_change_password(self, request):
        """Test that the password can be changed and is masked in the delta description."""
        request.json = {"password": "new password"}  # nosec
        response = post_source_location_parameter(SOURCE_LOCATION_ID, "password", self.database)
        self.assertTrue(response["ok"])
        self.assertEqual({}, response["availability"])
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual("new password", updated_report["source_locations"][SOURCE_LOCATION_ID]["password"])
        self.assert_delta(
            "changed the password of source location 'Source location' in report 'Report' "
            "from '********' to '************'.",
            [REPORT_ID, SOURCE_LOCATION_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
            updated_report,
        )

    def test_change_non_location_parameter(self, request):
        """Test that changing a parameter that is not a location parameter results in an error message."""
        request.json = {"tags": ["security"]}
        self.assertEqual(
            {"ok": False, "error": "Parameter 'tags' is not a source location parameter."},
            post_source_location_parameter(SOURCE_LOCATION_ID, "tags", self.database),
        )
        self.database.reports.insert_one.assert_not_called()

    def test_no_change(self, request):
        """Test that no new report is inserted when the parameter is unchanged."""
        request.json = {"url": "https://url"}
        response = post_source_location_parameter(SOURCE_LOCATION_ID, "url", self.database)
        self.assertEqual({"ok": True}, response)
        self.database.reports.insert_one.assert_not_called()

    def test_change_parameter_of_missing_source_location(self, request):
        """Test that changing a parameter of a missing source location results in an error message."""
        request.json = {"url": "https://new-url"}
        self.assert_missing_source_location(post_source_location_parameter(UNKNOWN_UUID, "url", self.database))
        self.database.reports.insert_one.assert_not_called()


class DeleteSourceLocationTest(SourceLocationTestCase):
    """Unit tests for the delete source location route."""

    def test_delete_source_location_in_use(self):
        """Test that a source location that is in use cannot be deleted."""
        self.assertEqual(
            {
                "ok": False,
                "error": f"Source location with UUID {SOURCE_LOCATION_ID} is in use by one or more sources.",
            },
            delete_source_location(SOURCE_LOCATION_ID, self.database),
        )
        self.database.reports.insert_one.assert_not_called()

    def test_delete_source_location(self):
        """Test that a source location that is not in use can be deleted."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        source["source_location"] = ""
        self.assertEqual({"ok": True}, delete_source_location(SOURCE_LOCATION_ID, self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual({}, updated_report["source_locations"])
        self.assert_delta(
            "deleted the source location 'Source location' from report 'Report'.",
            [REPORT_ID, SOURCE_LOCATION_ID],
            updated_report,
        )

    def test_delete_missing_source_location(self):
        """Test that deleting a missing source location results in an error message."""
        self.assert_missing_source_location(delete_source_location(UNKNOWN_UUID, self.database))
        self.database.reports.insert_one.assert_not_called()
