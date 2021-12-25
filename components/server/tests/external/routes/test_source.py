"""Unit tests for the source routes."""

import socket
import unittest
from unittest.mock import Mock, patch

import requests

from external.routes import (
    delete_source,
    post_move_source,
    post_source_attribute,
    post_source_copy,
    post_source_new,
    post_source_parameter,
)
from shared.model.report import Report

from ...fixtures import (
    METRIC_ID,
    METRIC_ID2,
    METRIC_ID3,
    METRIC_ID4,
    REPORT_ID,
    REPORT_ID2,
    SOURCE_ID,
    SOURCE_ID2,
    SOURCE_ID3,
    SOURCE_ID4,
    SOURCE_ID5,
    SOURCE_ID6,
    SOURCE_ID7,
    SUBJECT_ID,
    SUBJECT_ID2,
    SUBJECT_ID3,
    create_report,
)


class SourceTestCase(unittest.TestCase):  # skipcq: PTC-W0046
    """Common fixtures for the source route unit tests."""

    def setUp(self):
        """Override to set unit test fixtures."""
        self.url = "https://url"
        self.database = Mock()
        self.database.measurements.find.return_value = []
        self.email = "jenny@example.org"
        self.database.sessions.find_one.return_value = dict(user="Jenny", email=self.email)
        self.data_model = dict(
            _id="id",
            metrics=dict(metric_type=dict(default_source="source_type")),
            sources=dict(
                source_type=dict(
                    name="Source type",
                    parameters=dict(
                        url=dict(type="url", metrics=["metric_type"], default_value=""),
                        username=dict(type="string", metrics=["metric_type"], default_value=""),
                        password=dict(type="password", metrics=["metric_type"], default_value=""),
                        private_token=dict(type="password", metrics=["metric_type"], default_value=""),
                        choices=dict(
                            type="multiple_choice", metrics=["metric_type"], values=["A", "B", "C"], default_value=[]
                        ),
                        choices_with_addition=dict(
                            type="multiple_choice_with_addition", metrics=["metric_type"], values=[], default_value=[]
                        ),
                    ),
                ),
                new_source_type=dict(parameters={}),
            ),
        )
        self.sources = {
            SOURCE_ID: dict(name="Source", type="source_type", parameters=dict(username="username", choices=["D"])),
            SOURCE_ID2: dict(name="Source 2", type="source_type", parameters=dict(username="username")),
        }
        self.database.datamodels.find_one.return_value = self.data_model
        self.report = Report(
            self.data_model,
            dict(
                _id=REPORT_ID,
                title="Report",
                report_uuid=REPORT_ID,
                subjects={
                    SUBJECT_ID: dict(
                        name="Subject",
                        metrics={METRIC_ID: dict(name="Metric", type="metric_type", sources=self.sources)},
                    )
                },
            ),
        )
        self.database.reports.find.return_value = [self.report]

    def assert_delta(self, description: str, uuids=None, report=None) -> None:
        """Check that the report has the correct delta."""
        report = report or self.report
        self.assertEqual(dict(uuids=sorted(uuids) or [], email=self.email, description=description), report["delta"])


@patch("bottle.request")
class PostSourceAttributeTest(SourceTestCase):
    """Unit tests for the post source attribute route."""

    def assert_delta(self, description: str, uuids=None, report=None) -> None:
        """Extend to set up fixed parameters."""
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID] + (uuids or [SOURCE_ID])
        super().assert_delta(f"Jenny changed the {description}.", uuids, report)

    def test_name(self, request):
        """Test that the source name can be changed."""
        request.json = dict(name="New source name")
        self.assertEqual(dict(ok=True), post_source_attribute(SOURCE_ID, "name", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "name of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' from 'Source' to "
            "'New source name'",
            report=updated_report,
        )

    def test_post_source_type(self, request):
        """Test that the source type can be changed."""
        request.json = dict(type="new_source_type")
        self.assertEqual(dict(ok=True), post_source_attribute(SOURCE_ID, "type", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "type of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' from 'source_type' to "
            "'new_source_type'",
            report=updated_report,
        )

    def test_post_position(self, request):
        """Test that a metric can be moved."""
        request.json = dict(position="first")
        self.assertEqual(dict(ok=True), post_source_attribute(SOURCE_ID2, "position", self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assertEqual(
            [SOURCE_ID2, SOURCE_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].keys())
        )
        self.assert_delta(
            "position of source 'Source 2' of metric 'Metric' of subject 'Subject' in report 'Report' from '1' to '0'",
            [SOURCE_ID2],
            report=updated_report,
        )

    def test_no_change(self, request):
        """Test that no new report is inserted when the attribute is unchanged."""
        request.json = dict(name="Source")
        self.assertEqual(dict(ok=True), post_source_attribute(SOURCE_ID, "name", self.database))
        self.database.reports.insert_one.assert_not_called()


@patch("bottle.request")
class PostSourceParameterTest(SourceTestCase):
    """Unit tests for the post source parameter route."""

    STATUS_CODE = 200
    STATUS_CODE_REASON = "OK"

    def setUp(self):
        """Extend to add a report fixture."""
        super().setUp()
        self.report["subjects"][SUBJECT_ID2] = dict(
            name="Subject 2", metrics={METRIC_ID2: dict(name="Metric 2", type="metric_type", sources={})}
        )
        self.database.reports.find.return_value = [self.report]
        self.url_check_get_response = Mock(status_code=self.STATUS_CODE, reason=self.STATUS_CODE_REASON)

    def assert_url_check(self, response, status_code: int = None, status_code_reason: str = None):
        """Check the url check result."""
        status_code = status_code or self.STATUS_CODE
        status_code_reason = status_code_reason or self.STATUS_CODE_REASON
        availability = dict(
            status_code=status_code, reason=status_code_reason, source_uuid=SOURCE_ID, parameter_key="url"
        )
        self.assertEqual(dict(ok=True, availability=[availability]), response)

    def assert_delta(self, description: str, uuids=None, report=None) -> None:
        """Extend to set up fixed parameters."""
        uuids = uuids or [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID]
        description = f"Jenny changed the {description}."
        super().assert_delta(description, uuids, report)

    @patch.object(requests, "get")
    def test_url(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        self.database.reports.insert_one.assert_called_once_with(self.report)
        mock_get.assert_called_once_with(self.url, auth=("username", ""), headers={}, verify=False)
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
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response, -1, "RequestException")
        self.database.reports.insert_one.assert_called_once_with(self.report)
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
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response, -1, "[Errno 1234] Error message")
        self.database.reports.insert_one.assert_called_once_with(self.report)
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
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response, -1, "[Errno -2] Error message")
        self.database.reports.insert_one.assert_called_once_with(self.report)
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
        self.sources[SOURCE_ID]["parameters"]["password"] = "pwd"
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        self.database.reports.insert_one.assert_called_once_with(self.report)
        mock_get.assert_called_once_with(self.url, auth=("un", "pwd"), headers={}, verify=False)

    @patch.object(requests, "get")
    def test_url_no_url_type(self, mock_get, request):
        """Test that the source url can be changed and that the availability is not checked if it's not a url type."""
        self.data_model["sources"]["source_type"]["parameters"]["url"]["type"] = "string"
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url="unimportant")
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        mock_get.assert_not_called()

    def test_empty_url(self, request):
        """Test that the source url availability is not checked when the url is empty."""
        self.sources[SOURCE_ID]["parameters"]["url"] = self.url
        request.json = dict(url="")
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert_one.assert_called_once_with(self.report)

    @patch.object(requests, "get")
    def test_url_with_token(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url=self.url)
        self.sources[SOURCE_ID]["parameters"]["private_token"] = "xxx"
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        self.database.reports.insert_one.assert_called_once_with(self.report)
        mock_get.assert_called_once_with(self.url, auth=("xxx", ""), headers={"Private-Token": "xxx"}, verify=False)

    @patch.object(requests, "get")
    def test_urls_connection_on_update_other_field(self, mock_get, request):
        """Test that the all urls availability is checked when a parameter that it depends on is changed."""
        self.data_model["sources"]["source_type"]["parameters"]["url"]["validate_on"] = "password"
        mock_get.return_value = self.url_check_get_response
        request.json = dict(password="changed")
        self.sources[SOURCE_ID]["parameters"]["url"] = self.url
        response = post_source_parameter(SOURCE_ID, "password", self.database)
        self.assert_url_check(response)
        self.database.reports.insert_one.assert_called_once_with(self.report)

    def test_password(self, request):
        """Test that the password can be changed and is not logged."""
        request.json = dict(url="unimportant", password="secret")
        response = post_source_parameter(SOURCE_ID, "password", self.database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            """password of source 'Source' of metric 'Metric' of subject """
            """'Subject' in report 'Report' from '' to '******'""",
            report=updated_report,
        )

    def test_no_change(self, request):
        """Test that no new report is inserted if the parameter value is unchanged."""
        self.sources[SOURCE_ID]["parameters"]["url"] = self.url
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert_one.assert_not_called()

    def test_obsolete_multiple_choice_value(self, request):
        """Test that obsolete multiple choice values are removed."""
        parameters = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["parameters"]
        self.assertEqual(["D"], parameters["choices"])
        request.json = dict(choices=["A", "D"])
        response = post_source_parameter(SOURCE_ID, "choices", self.database)
        self.assertEqual(response, dict(ok=True))
        self.assertEqual(["A"], parameters["choices"])
        self.database.reports.insert_one.assert_called_once_with(self.report)

    def test_regexp_with_curly_braces(self, request):
        """Test that regular expressions with curly braces work.

        Curly braces shouldn't be interpreted as string formatting fields.
        """
        parameters = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["parameters"]
        request.json = dict(choices_with_addition=[r"[\w]{3}-[\w]{3}-[\w]{4}-[\w]{3}\/"])
        response = post_source_parameter(SOURCE_ID, "choices_with_addition", self.database)
        self.assertEqual(response, dict(ok=True))
        self.assertEqual([r"[\w]{3}-[\w]{3}-[\w]{4}-[\w]{3}\/"], parameters["choices_with_addition"])
        self.database.reports.insert_one.assert_called_once_with(self.report)
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "choices_with_addition of source 'Source' of metric 'Metric' of subject 'Subject' in report 'Report' "
            r"from '' to '['[\\w]{3}-[\\w]{3}-[\\w]{4}-[\\w]{3}\\/']'",
            report=updated_report,
        )


@patch("bottle.request")
class PostSourceParameterMassEditTest(SourceTestCase):
    """Unit tests for the mass edit variants of the post source parameter route."""

    UNCHANGED_VALUE = "different username"
    OLD_VALUE = "username"
    NEW_VALUE = "new username"

    def setUp(self):
        """Extend to add a report fixture."""
        super().setUp()
        self.sources[SOURCE_ID3] = dict(
            name="Source 3", type="source_type", parameters=dict(username=self.UNCHANGED_VALUE)
        )
        self.sources[SOURCE_ID4] = dict(
            name="Source 4", type="different_type", parameters=dict(username=self.OLD_VALUE)
        )
        self.sources2 = {
            SOURCE_ID5: dict(name="Source 5", type="source_type", parameters=dict(username=self.OLD_VALUE))
        }
        self.sources3 = {
            SOURCE_ID6: dict(name="Source 6", type="source_type", parameters=dict(username=self.OLD_VALUE))
        }
        self.sources4 = {
            SOURCE_ID7: dict(name="Source 7", type="source_type", parameters=dict(username=self.OLD_VALUE))
        }
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = dict(
            name="Metric 2", type="metric_type", sources=self.sources2
        )
        self.report["subjects"][SUBJECT_ID2] = dict(
            name="Subject 2", metrics={METRIC_ID3: dict(name="Metric 3", type="metric_type", sources=self.sources3)}
        )
        self.report2 = Report(
            self.data_model,
            dict(
                _id=REPORT_ID2,
                title="Report 2",
                report_uuid=REPORT_ID2,
                subjects={
                    SUBJECT_ID3: dict(
                        name="Subject 3",
                        metrics={METRIC_ID4: dict(name="Metric 4", type="metric_type", sources=self.sources4)},
                    )
                },
            ),
        )
        self.database.reports.find.return_value = [self.report, self.report2]

    def assert_value(self, value_sources_mapping):
        """Assert that the parameters have the correct value."""
        for value, sources in value_sources_mapping.items():
            for source in sources:
                self.assertEqual(value, source["parameters"]["username"])

    def assert_delta(self, description: str, uuids=None, report=None) -> None:
        """Extend to set up fixed parameters."""
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID, SOURCE_ID2] + (uuids or [])
        description = (
            f"Jenny changed the username of all sources of type 'Source type' with username 'username' {description}."
        )
        super().assert_delta(description, uuids, report)

    def test_mass_edit_reports(self, request):
        """Test that a source parameter can be mass edited."""
        request.json = dict(username=self.NEW_VALUE, edit_scope="reports")
        response = post_source_parameter(SOURCE_ID, "username", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert_many.assert_called_once_with((self.report, self.report2), ordered=False)
        self.assert_value(
            {
                self.NEW_VALUE: [
                    self.sources[SOURCE_ID],
                    self.sources[SOURCE_ID2],
                    self.sources2[SOURCE_ID5],
                    self.sources3[SOURCE_ID6],
                    self.sources4[SOURCE_ID7],
                ],
                self.OLD_VALUE: [self.sources[SOURCE_ID4]],
                self.UNCHANGED_VALUE: [self.sources[SOURCE_ID3]],
            }
        )
        uuids = [
            REPORT_ID2,
            SUBJECT_ID2,
            SUBJECT_ID3,
            METRIC_ID2,
            METRIC_ID3,
            METRIC_ID4,
            SOURCE_ID5,
            SOURCE_ID6,
            SOURCE_ID7,
        ]
        updated_reports = self.database.reports.insert_many.call_args[0][0]
        ipdated_report_1 = updated_reports[0]
        ipdated_report_2 = updated_reports[1]
        self.assert_delta("in all reports from 'username' to 'new username'", uuids, ipdated_report_1)
        self.assert_delta("in all reports from 'username' to 'new username'", uuids, ipdated_report_2)

    def test_mass_edit_report(self, request):
        """Test that a source parameter can be mass edited."""
        request.json = dict(username=self.NEW_VALUE, edit_scope="report")
        response = post_source_parameter(SOURCE_ID, "username", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert_one.assert_called_once_with(self.report)
        self.assert_value(
            {
                self.NEW_VALUE: [
                    self.sources[SOURCE_ID],
                    self.sources[SOURCE_ID2],
                    self.sources2[SOURCE_ID5],
                    self.sources3[SOURCE_ID6],
                ],
                self.OLD_VALUE: [self.sources[SOURCE_ID4]],
                self.UNCHANGED_VALUE: [self.sources[SOURCE_ID3]],
            }
        )
        extra_uuids = [METRIC_ID2, SOURCE_ID5, SUBJECT_ID2, METRIC_ID3, SOURCE_ID6]
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta("in report 'Report' from 'username' to 'new username'", extra_uuids, updated_report)

    def test_mass_edit_subject(self, request):
        """Test that a source parameter can be mass edited."""
        request.json = dict(username=self.NEW_VALUE, edit_scope="subject")
        response = post_source_parameter(SOURCE_ID, "username", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert_one.assert_called_once_with(self.report)
        self.assert_value(
            {
                self.NEW_VALUE: [self.sources[SOURCE_ID], self.sources[SOURCE_ID2], self.sources2[SOURCE_ID5]],
                self.OLD_VALUE: [self.sources[SOURCE_ID4], self.sources3[SOURCE_ID6]],
                self.UNCHANGED_VALUE: [self.sources[SOURCE_ID3]],
            }
        )
        extra_uuids = [METRIC_ID2, SOURCE_ID5]
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "of subject 'Subject' in report 'Report' from 'username' to 'new username'", extra_uuids, updated_report
        )

    def test_mass_edit_metric(self, request):
        """Test that a source parameter can be mass edited."""
        request.json = dict(username=self.NEW_VALUE, edit_scope="metric")
        response = post_source_parameter(SOURCE_ID, "username", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert_one.assert_called_once_with(self.report)
        self.assert_value(
            {
                self.NEW_VALUE: [self.sources[SOURCE_ID], self.sources[SOURCE_ID2]],
                self.OLD_VALUE: [self.sources[SOURCE_ID4], self.sources2[SOURCE_ID5], self.sources3[SOURCE_ID6]],
                self.UNCHANGED_VALUE: [self.sources[SOURCE_ID3]],
            }
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(
            "of metric 'Metric' of subject 'Subject' in report 'Report' from 'username' to 'new username'",
            report=updated_report,
        )


class SourceTest(SourceTestCase):
    """Unit tests for adding and deleting sources."""

    def setUp(self):
        """Extend to add a report fixture."""
        super().setUp()
        self.report = Report(None, create_report())
        self.database.reports.find.return_value = [self.report]
        self.target_metric_name = "Target metric"

    def test_add_source(self):
        """Test that a new source is added."""
        self.assertTrue(post_source_new(METRIC_ID, self.database)["ok"])
        self.database.reports.insert_one.assert_called_once_with(self.report)
        source_uuid = list(self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].keys())[1]
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID, source_uuid]
        description = "Jenny added a new source to metric 'Metric' of subject 'Subject' in report 'Report'."
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(description, uuids, updated_report)

    def test_copy_source(self):
        """Test that a source can be copied."""
        self.assertTrue(post_source_copy(SOURCE_ID, METRIC_ID, self.database)["ok"])
        self.database.reports.insert_one.assert_called_once_with(self.report)
        copied_source_uuid, copied_source = list(
            self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].items()
        )[1]
        self.assertEqual("Source (copy)", copied_source["name"])
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID, copied_source_uuid]
        description = (
            "Jenny copied the source 'Source' of metric 'Metric' of subject 'Subject' from report 'Report' to metric "
            "'Metric' of subject 'Subject' in report 'Report'."
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(description, uuids, updated_report)

    def test_move_source_within_subject(self):
        """Test that a source can be moved to a different metric in the same subject."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        target_metric = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = dict(
            name=self.target_metric_name, type="metric_type", sources={}
        )
        self.assertEqual(dict(ok=True), post_move_source(SOURCE_ID, METRIC_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        self.assertEqual((SOURCE_ID, source), next(iter(target_metric["sources"].items())))
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID, METRIC_ID2, SOURCE_ID]
        description = (
            f"Jenny moved the source 'Source' from metric 'Metric' of subject 'Subject' in report 'Report' to metric "
            f"'{self.target_metric_name}' of subject 'Subject' in report 'Report'."
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(description, uuids, updated_report)

    def test_move_source_within_report(self):
        """Test that a source can be moved to a different metric in the same report."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        target_metric = dict(name=self.target_metric_name, type="metric_type", sources={})
        target_subject = dict(name="Target subject", metrics={METRIC_ID2: target_metric})
        self.report["subjects"][SUBJECT_ID2] = target_subject
        self.assertEqual(dict(ok=True), post_move_source(SOURCE_ID, METRIC_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        self.assertEqual((SOURCE_ID, source), next(iter(target_metric["sources"].items())))
        uuids = [REPORT_ID, SUBJECT_ID, SUBJECT_ID2, METRIC_ID, METRIC_ID2, SOURCE_ID]
        description = (
            f"Jenny moved the source 'Source' from metric 'Metric' of subject 'Subject' in report 'Report' to metric "
            f"'{self.target_metric_name}' of subject 'Target subject' in report 'Report'."
        )
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(description, uuids, updated_report)

    def test_move_source_across_reports(self):
        """Test that a source can be moved to a different metric in a different report."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        target_metric = dict(name=self.target_metric_name, type="metric_type", sources={})
        target_subject = dict(name="Target subject", metrics={METRIC_ID2: target_metric})
        target_report = dict(
            _id="target_report", title="Target report", report_uuid=REPORT_ID2, subjects={SUBJECT_ID2: target_subject}
        )
        self.database.reports.find.return_value = [self.report, target_report]
        self.assertEqual(dict(ok=True), post_move_source(SOURCE_ID, METRIC_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        self.assertEqual((SOURCE_ID, source), next(iter(target_metric["sources"].items())))
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

    def test_delete_source(self):
        """Test that the source can be deleted."""
        self.assertEqual(dict(ok=True), delete_source(SOURCE_ID, self.database))
        self.database.reports.insert_one.assert_called_once_with(self.report)
        uuids = [REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID]
        description = "Jenny deleted the source 'Source' from metric 'Metric' of subject 'Subject' in report 'Report'."
        updated_report = self.database.reports.insert_one.call_args[0][0]
        self.assert_delta(description, uuids, updated_report)
