"""Unit tests for the source routes."""

import socket
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import requests
from shared.model.metric import Metric

from shared.model.report import Report
from shared.utils.functions import first

from routes import (
    delete_source,
    post_move_source,
    post_source_attribute,
    post_source_copy,
    post_source_new,
    post_source_parameter,
)

from tests.fixtures import (
    METRIC_ID,
    METRIC_ID2,
    METRIC_ID3,
    REPORT_ID,
    REPORT_ID2,
    SOURCE_ID,
    SOURCE_ID2,
    SOURCE_ID3,
    SOURCE_LOCATION_ID,
    SUBJECT_ID,
    SUBJECT_ID2,
    create_report,
    create_source_location,
)

from tests.base import DataModelTestCase

if TYPE_CHECKING:
    from shared.utils.type import SourceId


class SourceTestCase(DataModelTestCase):
    """Common fixtures for the source route unit tests."""

    def setUp(self):
        """Override to set up unit test fixtures."""
        super().setUp()
        self.url = "https://url"
        self.database.measurements.find.return_value = []
        self.email = "jenny@example.org"
        self.database.sessions.find_one.return_value = {"user": "Jenny", "email": self.email}
        self.sources = {
            SOURCE_ID: {
                "name": "Source",
                "type": "owasp_zap",
                "parameters": {"username": "username", "risks": ["high", "blocker"]},
            },
            SOURCE_ID2: {"name": "Source 2", "type": "owasp_zap", "parameters": {"username": "username"}},
        }
        report_dict = {
            "_id": REPORT_ID,
            "title": "Report",
            "report_uuid": REPORT_ID,
            "subjects": {
                SUBJECT_ID: {
                    "name": "Subject",
                    "metrics": {METRIC_ID: {"name": "Metric", "type": "security_warnings", "sources": self.sources}},
                },
            },
        }
        self.report = Report(self.DATA_MODEL, report_dict)
        self.database.reports.find.return_value = [report_dict]

    def assert_delta(self, description: str, uuids=None, report=None) -> None:
        """Check that the report has the correct delta."""
        report = report or self.report
        self.assertEqual(
            {"uuids": sorted(uuids or []), "email": self.email, "description": description},
            report["delta"],
        )


@patch("bottle.request")
class PostSourceAttributeTest(SourceTestCase):
    """Unit tests for the post source attribute route."""

    def assert_delta(self, description: str, uuids=None, report=None) -> None:
        """Extend to add common information to the assertion checking the changelog entry."""
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID] + (uuids or [SOURCE_ID])
        super().assert_delta(f"Jenny changed the {description}.", uuids, report)

    def test_name(self, request):
        """Test that the source name can be changed."""
        request.json = {"name": "New source name"}
        self.assertEqual({"ok": True}, post_source_attribute(SOURCE_ID, "name", self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "name of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' from 'Source' to "
            "'New source name'",
            report=updated_report,
        )

    def test_post_new_source_type(self, request):
        """Test that the source type can be changed."""
        request.json = {"type": "ojaudit"}
        self.assertEqual({"ok": True}, post_source_attribute(SOURCE_ID, "type", self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "type of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' from 'owasp_zap' to "
            "'ojaudit'",
            report=updated_report,
        )

    def test_post_position(self, request):
        """Test that a metric can be moved."""
        request.json = {"position": "first"}
        self.assertEqual({"ok": True}, post_source_attribute(SOURCE_ID2, "position", self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual(
            [SOURCE_ID2, SOURCE_ID],
            list(self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].keys()),
        )
        self.assert_delta(
            "position of source 'Source 2' of metric 'Metric' of subject 'Subject' in report 'Report' from '1' to '0'",
            [SOURCE_ID2],
            report=updated_report,
        )

    def test_no_change(self, request):
        """Test that no new report is inserted when the attribute is unchanged."""
        request.json = {"name": "Source"}
        self.assertEqual({"ok": True}, post_source_attribute(SOURCE_ID, "name", self.database))
        self.database.reports.insert_one.assert_not_called()

    def test_post_source_type_with_location(self, request):
        """Test that changing the source type to a type with locations resets the source location."""
        self.sources[SOURCE_ID]["source_location"] = SOURCE_LOCATION_ID
        request.json = {"type": "ojaudit"}
        self.assertEqual({"ok": True}, post_source_attribute(SOURCE_ID, "type", self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        source = updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        self.assertEqual("", source["source_location"])

    def test_post_source_type_without_location(self, request):
        """Test that changing the source type to a type without locations removes the source location."""
        self.sources[SOURCE_ID]["source_location"] = SOURCE_LOCATION_ID
        request.json = {"type": "manual_number"}
        self.assertEqual({"ok": True}, post_source_attribute(SOURCE_ID, "type", self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        source = updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        self.assertNotIn("source_location", source)


@patch("bottle.request")
class PostSourceParameterTest(SourceTestCase):
    """Unit tests for the post source parameter route."""

    STATUS_CODE = 200
    STATUS_CODE_REASON = "OK"

    def setUp(self):
        """Extend to add a report fixture."""
        super().setUp()
        self.report["subjects"][SUBJECT_ID2] = {
            "name": "Subject 2",
            "metrics": {
                METRIC_ID2: {"name": "Metric 2", "type": "security_warnings", "sources": {}},
                METRIC_ID3: {
                    "type": "issues",
                    "sources": {SOURCE_ID3: {"type": "jira", "parameters": {"private_token": "xxx"}}},  # nosec
                },
            },
        }
        self.url_check_get_response = Mock(status_code=self.STATUS_CODE, reason=self.STATUS_CODE_REASON)

    def assert_url_check(
        self,
        response,
        status_code: int | None = None,
        status_code_reason: str | None = None,
        source_uuid: SourceId = SOURCE_ID,
    ):
        """Check the url check result."""
        status_code = status_code or self.STATUS_CODE
        status_code_reason = status_code_reason or self.STATUS_CODE_REASON
        availability = {
            "status_code": status_code,
            "reason": status_code_reason,
            "source_uuid": source_uuid,
            "parameter_key": "url",
        }
        self.assertEqual({"ok": True, "availability": availability}, response)

    def assert_delta(self, description: str, uuids=None, report=None) -> None:
        """Extend to set up fixed parameters."""
        uuids = uuids or [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID]
        description = f"Jenny changed the {description}."
        super().assert_delta(description, uuids, report)

    @patch.object(requests, "get")
    def test_url(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        mock_get.return_value = self.url_check_get_response
        request.json = {"url": self.url}
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        mock_get.assert_called_once_with(self.url, auth=("username", ""), headers={}, timeout=10)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        url = self.url
        self.assert_delta(
            f"url of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' from '' to '{url}'",
            report=updated_report,
        )

    @patch.object(requests, "get")
    def test_url_http_error(self, mock_get, request):
        """Test that the error is reported if a request exception occurs, while checking connection of a url."""
        mock_get.side_effect = requests.exceptions.RequestException
        request.json = {"url": self.url}
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response, -1, "RequestException")
        updated_report = self.database.reports.insert_one.call_args[0][0]
        url = self.url
        self.assert_delta(
            f"url of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' from '' to '{url}'",
            report=updated_report,
        )

    @patch.object(requests, "get")
    def test_url_socket_error(self, mock_get, request):
        """Test that the error is reported if a request exception occurs, while checking connection of a url."""
        mock_get.side_effect = socket.gaierror("This is some text that should be ignored ([Errno 1234] Error message)")
        request.json = {"url": self.url}
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response, -1, "[Errno 1234] Error message")
        updated_report = self.database.reports.insert_one.call_args[0][0]
        url = self.url
        self.assert_delta(
            f"url of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' from '' to '{url}'",
            report=updated_report,
        )

    @patch.object(requests, "get")
    def test_url_socket_error_negative_errno(self, mock_get, request):
        """Test that the error is reported if a request exception occurs with negative errno."""
        mock_get.side_effect = socket.gaierror("This is some text that should be ignored ([Errno -2] Error message)")
        request.json = {"url": self.url}
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response, -1, "[Errno -2] Error message")
        updated_report = self.database.reports.insert_one.call_args[0][0]
        url = self.url
        self.assert_delta(
            f"url of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' from '' to '{url}'",
            report=updated_report,
        )

    @patch.object(requests, "get")
    def test_url_with_user(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        self.sources[SOURCE_ID]["parameters"]["username"] = "un"
        self.sources[SOURCE_ID]["parameters"]["password"] = "pwd"  # nosec
        mock_get.return_value = self.url_check_get_response
        request.json = {"url": self.url}
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        mock_get.assert_called_once_with(self.url, auth=("un", "pwd"), headers={}, timeout=10)

    @patch.object(requests, "get")
    def test_url_no_url_type(self, mock_get, request):
        """Test that the landing url can be changed but that availability is not checked because it's not a url type."""
        mock_get.return_value = self.url_check_get_response
        request.json = {"landing_url": "unimportant"}
        response = post_source_parameter(SOURCE_ID, "landing_url", self.database)
        self.assertEqual(response, {"ok": True, "availability": {}})
        mock_get.assert_not_called()

    @patch.object(requests, "get")
    def test_empty_url(self, mock_get, request):
        """Test that the source url availability is not checked when the url is empty."""
        self.sources[SOURCE_ID]["parameters"]["url"] = self.url
        request.json = {"url": ""}
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assertEqual(response, {"ok": True, "availability": {}})
        mock_get.assert_not_called()

    @patch.object(requests, "get")
    def test_url_with_token(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        mock_get.return_value = self.url_check_get_response
        request.json = {"url": self.url}
        self.sources[SOURCE_ID]["parameters"]["private_token"] = "xxx"  # nosec
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        mock_get.assert_called_once_with(
            self.url,
            auth=("xxx", ""),
            headers={"Private-Token": "xxx", "Authorization": "Bearer xxx"},
            timeout=10,
        )

    @patch.object(requests, "get")
    def test_url_with_token_and_validation_path(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        mock_get.return_value = self.url_check_get_response
        request.json = {"url": self.url}
        response = post_source_parameter(SOURCE_ID3, "url", self.database)
        self.assert_url_check(response, source_uuid=SOURCE_ID3)
        mock_get.assert_called_once_with(
            self.url + "/rest/api/2/myself",
            auth=None,
            headers={"Private-Token": "xxx", "Authorization": "Bearer xxx"},
            timeout=10,
        )

    @patch.object(requests, "get")
    def test_urls_connection_on_update_other_field(self, mock_get, request):
        """Test that the url availability is checked when a parameter that it depends on is changed."""
        mock_get.return_value = self.url_check_get_response
        request.json = {"password": "changed"}  # nosec
        self.sources[SOURCE_ID]["parameters"]["url"] = self.url
        response = post_source_parameter(SOURCE_ID, "password", self.database)
        self.assert_url_check(response)

    def test_password(self, request):
        """Test that the password can be changed and is not logged."""
        request.json = {"password": "secret"}  # nosec
        response = post_source_parameter(SOURCE_ID, "password", self.database)
        self.assertEqual(response, {"ok": True, "availability": {}})
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            """password of source 'Source' of metric 'Metric' of subject """
            """'Subject' in report 'Report' from '' to '******'""",
            report=updated_report,
        )

    def test_no_change(self, request):
        """Test that no new report is inserted if the parameter value is unchanged."""
        self.sources[SOURCE_ID]["parameters"]["url"] = self.url
        request.json = {"url": self.url}
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assertEqual({"ok": True}, response)
        self.database.reports.insert_one.assert_not_called()

    def test_obsolete_multiple_choice_value(self, request):
        """Test that obsolete multiple choice values are removed."""
        parameters = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["parameters"]
        self.assertEqual(["high", "blocker"], parameters["risks"])
        request.json = {"risks": ["medium", "high", "critical"]}
        response = post_source_parameter(SOURCE_ID, "risks", self.database)
        self.assertEqual(response, {"ok": True, "availability": {}})
        self.assertEqual(["medium", "high"], parameters["risks"])

    def test_regexp_with_curly_braces(self, request):
        """Test that regular expressions with curly braces work.

        Curly braces shouldn't be interpreted as string formatting fields.
        """
        parameters = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["parameters"]
        request.json = {"variable_url_regexp": [r"[\w]{3}-[\w]{3}-[\w]{4}-[\w]{3}\/"]}
        response = post_source_parameter(SOURCE_ID, "variable_url_regexp", self.database)
        self.assertEqual(response, {"ok": True, "availability": {}})
        self.assertEqual([r"[\w]{3}-[\w]{3}-[\w]{4}-[\w]{3}\/"], parameters["variable_url_regexp"])
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "variable_url_regexp of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' "
            r"from '' to '['[\\w]{3}-[\\w]{3}-[\\w]{4}-[\\w]{3}\\/']'",
            report=updated_report,
        )


class SourceTest(SourceTestCase):
    """Unit tests for adding and deleting sources."""

    def setUp(self):
        """Extend to add a report fixture."""
        super().setUp()
        self.report = Report(self.DATA_MODEL, report_dict := create_report())
        self.database.reports.find.return_value = [report_dict]
        self.target_metric_name = "Target metric"

    @patch("bottle.request")
    def test_add_source(self, request):
        """Test that a new source is added."""
        request.json = {"type": "ojaudit"}
        self.assertTrue(post_source_new(METRIC_ID, self.database)["ok"])
        updated_report = self.database.reports.insert_one.call_args[0][0]
        source_uuid = list(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].keys())[1]
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID, source_uuid]
        description = "Jenny added a new source to metric 'Metric' of subject 'Subject' in report 'Report'."
        self.assert_delta(description, uuids, updated_report)
        new_source = updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][source_uuid]
        self.assertEqual("ojaudit", new_source["type"])
        self.assertEqual("", new_source["source_location"])

    @patch("bottle.request")
    def test_add_source_without_location(self, request):
        """Test that a new source of a type without locations does not get a source location reference."""
        request.json = {"type": "manual_number"}
        self.assertTrue(post_source_new(METRIC_ID, self.database)["ok"])
        updated_report = self.database.reports.insert_one.call_args[0][0]
        source_uuid = list(updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].keys())[1]
        new_source = updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][source_uuid]
        self.assertEqual("manual_number", new_source["type"])
        self.assertNotIn("source_location", new_source)

    @patch("bottle.request")
    def test_change_source_location(self, request):
        """Test that the source location of a source can be changed."""
        request.json = {"source_location": ""}
        self.assertEqual({"ok": True}, post_source_attribute(SOURCE_ID, "source_location", self.database))
        updated_report = self.database.reports.insert_one.call_args[0][0]
        source = updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        self.assertEqual("", source["source_location"])
        description = (
            "Jenny changed the source_location of source 'Source' of metric 'Metric' of subject 'Subject' in report "
            "'Report' from 'Source location' to ''."
        )
        self.assert_delta(description, [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID], updated_report)

    def test_copy_source(self):
        """Test that a source can be copied."""
        self.assertTrue(post_source_copy(SOURCE_ID, METRIC_ID, self.database)["ok"])
        updated_report = self.database.reports.insert_one.call_args[0][0]
        copied_source_uuid, copied_source = list(
            updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].items(),
        )[1]
        self.assertEqual("Source", copied_source["name"])
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID, copied_source_uuid]
        description = (
            "Jenny copied the source 'Source' of metric 'Metric' of subject 'Subject' from report 'Report' to metric "
            "'Metric' of subject 'Subject' in report 'Report'."
        )
        self.assert_delta(description, uuids, updated_report)

    def test_move_source_within_subject(self):
        """Test that a source can be moved to a different metric in the same subject."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        target_metric = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = Metric(
            self.DATA_MODEL,
            {"name": self.target_metric_name, "type": "security_warnings", "sources": {}},
            METRIC_ID2,
            SUBJECT_ID,
        )
        self.assertEqual({"ok": True}, post_move_source(SOURCE_ID, METRIC_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        self.assertEqual((SOURCE_ID, source), next(iter(target_metric["sources"].items())))
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID, METRIC_ID2, SOURCE_ID]
        description = (
            "Jenny moved the source 'Source' from metric 'Metric' of subject 'Subject' in report 'Report' to metric "
            f"'{self.target_metric_name}' of subject 'Subject' in report 'Report'."
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(description, uuids, updated_report)

    def test_move_source_within_report(self):
        """Test that a source can be moved to a different metric in the same report."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        target_metric = {"name": self.target_metric_name, "type": "security_warnings", "sources": {}}
        target_subject = {"name": "Target subject", "metrics": {METRIC_ID2: target_metric}}
        self.report["subjects"][SUBJECT_ID2] = target_subject
        self.assertEqual({"ok": True}, post_move_source(SOURCE_ID, METRIC_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        self.assertEqual((SOURCE_ID, source), next(iter(target_metric["sources"].items())))
        uuids = [REPORT_ID, SUBJECT_ID, SUBJECT_ID2, METRIC_ID, METRIC_ID2, SOURCE_ID]
        description = (
            "Jenny moved the source 'Source' from metric 'Metric' of subject 'Subject' in report 'Report' to metric "
            f"'{self.target_metric_name}' of subject 'Target subject' in report 'Report'."
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(description, uuids, updated_report)

    def test_move_source_across_reports(self):
        """Test that a source can be moved to a different metric in a different report."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        target_metric = {"name": self.target_metric_name, "type": "security_warnings", "sources": {}}
        target_subject = {"name": "Target subject", "metrics": {METRIC_ID2: target_metric}}
        target_report = {
            "_id": "target_report",
            "title": "Target report",
            "report_uuid": REPORT_ID2,
            "subjects": {SUBJECT_ID2: target_subject},
        }
        self.database.reports.find.return_value = [self.report, target_report]
        self.assertEqual({"ok": True}, post_move_source(SOURCE_ID, METRIC_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        moved_source_uuid, moved_source = next(iter(target_metric["sources"].items()))
        self.assertEqual(SOURCE_ID, moved_source_uuid)
        self.assertEqual(
            {key: value for key, value in source.items() if key != "source_location"},
            {key: value for key, value in moved_source.items() if key != "source_location"},
        )
        expected_description = (
            "Jenny moved the source 'Source' from metric 'Metric' of subject 'Subject' in report "
            f"'Report' to metric '{self.target_metric_name}' of subject 'Target subject' in "
            "report 'Target report'."
        )
        expected_uuids = [REPORT_ID, REPORT_ID2, SUBJECT_ID, SUBJECT_ID2, METRIC_ID, METRIC_ID2, SOURCE_ID]

        updated_reports = self.database.reports.insert_many.call_args[0][0]
        updated_target_report = updated_reports[0]
        updated_source_report = updated_reports[1]
        self.assert_delta(expected_description, expected_uuids, updated_source_report)
        self.assert_delta(expected_description, expected_uuids, updated_target_report)
        # The source location referenced by the moved source is imported into the target report under a new uuid:
        imported_location_uuid, imported_location = first(updated_target_report["source_locations"].items())
        self.assertNotEqual(SOURCE_LOCATION_ID, imported_location_uuid)
        self.assertEqual(create_source_location(), imported_location)
        self.assertEqual(imported_location_uuid, moved_source["source_location"])

    def test_delete_source(self):
        """Test that the source can be deleted."""
        self.assertEqual({"ok": True}, delete_source(SOURCE_ID, self.database))
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID]
        description = "Jenny deleted the source 'Source' from metric 'Metric' of subject 'Subject' in report 'Report'."
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual({}, updated_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        self.assert_delta(description, uuids, updated_report)
