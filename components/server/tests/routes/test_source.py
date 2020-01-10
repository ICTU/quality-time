"""Unit tests for the source routes."""

import unittest
from unittest.mock import Mock, patch

import requests

from routes.source import delete_source, post_source_attribute, post_source_copy, post_source_new, post_source_parameter

from .fixtures import METRIC_ID, REPORT_ID, SOURCE_ID, SOURCE_ID2, SUBJECT_ID, create_report


@patch("bottle.request")
class PostSourceAttributeTest(unittest.TestCase):
    """Unit tests for the post source attribute route."""

    def setUp(self):
        self.sources = {
            SOURCE_ID: dict(name="Source", type="type", parameters=dict()),
            SOURCE_ID2: dict(name="Source 2", type="type", parameters=dict())}
        self.report = dict(
            _id=REPORT_ID, title="Report", report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID: dict(
                    name="Subject",
                    metrics={
                        METRIC_ID: dict(
                            name="Metric", type="type", sources=self.sources)})})
        self.database = Mock()
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.reports.find_one.return_value = self.report
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="id", metrics=dict(type=dict()), sources=dict(type=dict(name="Type"), new_type=dict(parameters=dict())))
        self.database.measurements.find.return_value = []

    def test_name(self, request):
        """Test that the source name can be changed."""
        request.json = dict(name="New source name")
        self.assertEqual(dict(ok=True), post_source_attribute(SOURCE_ID, "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
                 description="Jenny changed the name of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from 'Source' to 'New source name'."),
            self.report["delta"])

    def test_post_source_type(self, request):
        """Test that the source type can be changed."""
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_source_attribute(SOURCE_ID, "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
                 description="Jenny changed the type of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from 'type' to 'new_type'."),
            self.report["delta"])

    def test_post_position(self, request):
        """Test that a metric can be moved."""
        request.json = dict(position="first")
        self.assertEqual(dict(ok=True), post_source_attribute(SOURCE_ID2, "position", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            [SOURCE_ID2, SOURCE_ID], list(self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].keys()))
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID2],
                 description="Jenny changed the position of source 'Source 2' of metric 'Metric' of subject 'Subject' "
                             "in report 'Report' from '1' to '0'."),
            self.report["delta"])

    def test_no_change(self, request):
        """Test that no new report is inserted when the attribute is unchanged."""
        request.json = dict(name="Source")
        self.assertEqual(dict(ok=True), post_source_attribute(SOURCE_ID, "name", self.database))
        self.database.reports.insert.assert_not_called()


@patch("bottle.request")
class PostSourceParameterTest(unittest.TestCase):
    """Unit tests for the post source parameter route."""

    STATUS_CODE = 200
    STATUS_CODE_REASON = "OK"

    def setUp(self):
        self.url = "https://url"
        self.sources = {
            SOURCE_ID: dict(name="Source", type="type", parameters=dict()),
            SOURCE_ID2: dict(name="Source 2", type="type", parameters=dict())}
        self.report = dict(
            _id=REPORT_ID, title="Report", report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID: dict(
                    name="Subject",
                    metrics={METRIC_ID: dict(name="Metric", type="type", sources=self.sources)})})
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.reports.find_one.return_value = self.report
        self.datamodel = dict(
            _id="id",
            metrics=dict(type=dict()),
            sources=dict(
                type=dict(
                    parameters=dict(
                        url=dict(type="url"), username=dict(type="string"), password=dict(type="password")))))
        self.database.datamodels.find_one.return_value = self.datamodel
        self.database.measurements.find.return_value = []
        self.url_check_get_response = Mock(status_code=self.STATUS_CODE, reason=self.STATUS_CODE_REASON)

    def assert_url_check(self, response, status_code: int = None, status_code_reason: str = None):
        """Check the url check result."""
        status_code = status_code or self.STATUS_CODE
        status_code_reason = status_code_reason or self.STATUS_CODE_REASON
        self.assertEqual(
            response,
            dict(
                ok=True,
                availability=[
                    dict(
                        status_code=status_code, reason=status_code_reason, source_uuid=SOURCE_ID,
                        parameter_key="url")]))

    @patch.object(requests, 'get')
    def test_url(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_called_once_with(self.url, auth=None)
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
                 description="Jenny changed the url of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             f"report 'Report' from '' to '{self.url}'."),
            self.report["delta"])

    @patch.object(requests, 'get')
    def test_url_http_error(self, mock_get, request):
        """Test that the error is reported if a request exception occurs, while checking connection of a url."""
        mock_get.side_effect = requests.exceptions.RequestException
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response, -1, "Unknown error")
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
                 description="Jenny changed the url of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             f"report 'Report' from '' to '{self.url}'."),
            self.report["delta"])

    @patch.object(requests, 'get')
    def test_url_with_user(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        self.sources[SOURCE_ID]['parameters']['username'] = 'un'
        self.sources[SOURCE_ID]['parameters']['password'] = 'pwd'
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_called_once_with(self.url, auth=('un', 'pwd'))

    @patch.object(requests, 'get')
    def test_url_no_url_type(self, mock_get, request):
        """Test that the source url can be changed and that the availability is not checked if it's not a url type."""
        self.datamodel["sources"]["type"]["parameters"]["url"]["type"] = "string"
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url="unimportant")
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_not_called()

    def test_empty_url(self, request):
        """Test that the source url availability is not checked when the url is empty."""
        self.sources[SOURCE_ID]["parameters"]["url"] = self.url
        request.json = dict(url="")
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert.assert_called_once_with(self.report)

    @patch.object(requests, 'get')
    def test_url_with_token(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url=self.url)
        self.sources[SOURCE_ID]['parameters']['private_token'] = 'xxx'
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_called_once_with(self.url, auth=('xxx', ''))

    @patch.object(requests, 'get')
    def test_urls_connection_on_update_other_field(self, mock_get, request):
        """Test that the all urls availability is checked when a parameter that it depends on is changed."""
        self.datamodel["sources"]["type"]["parameters"]["url"]["validate_on"] = "password"
        mock_get.return_value = self.url_check_get_response
        request.json = dict(password="changed")
        self.sources[SOURCE_ID]['parameters']['url'] = self.url
        response = post_source_parameter(SOURCE_ID, "password", self.database)
        self.assert_url_check(response)
        self.database.reports.insert.assert_called_once_with(self.report)

    def test_password(self, request):
        """Test that the password can be changed and is not logged."""
        request.json = dict(url="unimportant", password="secret")
        response = post_source_parameter(SOURCE_ID, "password", self.database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
                 description="Jenny changed the password of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from '' to '******'."),
            self.report["delta"])

    def test_no_change(self, request):
        """Test that no new report is inserted if the parameter value is unchanged."""
        self.sources[SOURCE_ID]["parameters"]["url"] = self.url
        request.json = dict(url=self.url)
        response = post_source_parameter(SOURCE_ID, "url", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert.assert_not_called()


class SourceTest(unittest.TestCase):
    """Unit tests for adding and deleting sources."""

    def setUp(self):
        self.database = Mock()
        self.database.measurements.find.return_value = []
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="",
            metrics=dict(metric_type=dict(name="Metric type", direction="<", default_source="source_type")),
            sources=dict(source_type=dict(name="Source type", parameters=dict())))
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.reports.find_one.return_value = self.report = create_report()

    def test_add_source(self):
        """Test that a new source is added."""
        self.assertEqual(dict(ok=True), post_source_new(METRIC_ID, self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        source_uuid = list(self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].keys())[1]
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, source_uuid],
                 description="Jenny added a new source to metric 'Metric' of subject 'Subject' in report "
                             "'Report'."),
            self.report["delta"])

    def test_copy_source(self):
        """Test that a source can be copied."""
        self.assertEqual(dict(ok=True), post_source_copy(SOURCE_ID, self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        copied_source_uuid, copied_source = list(
            self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"].items())[1]
        self.assertEqual("Source (copy)", copied_source["name"])
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID, copied_source_uuid],
                 description="Jenny copied the source 'Source' of metric 'Metric' of subject 'Subject' in report "
                             "'Report'."),
            self.report["delta"])

    def test_delete_source(self):
        """Test that the source can be deleted."""
        self.assertEqual(dict(ok=True), delete_source(SOURCE_ID, self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
                 description="Jenny deleted the source 'Source' from metric 'Metric' of subject 'Subject' in "
                             "report 'Report'."),
            self.report["delta"])
