"""Unit tests for the source routes."""

import unittest
from unittest.mock import Mock, patch

import requests

from routes.source import delete_source, post_source_attribute, post_source_copy, post_source_new, post_source_parameter

from .fixtures import METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID


@patch("bottle.request")
class PostSourceAttributeTest(unittest.TestCase):
    """Unit tests for the post source attribute route."""

    def setUp(self):
        self.report = dict(
            _id=REPORT_ID, title="Report",
            subjects={
                SUBJECT_ID: dict(
                    name="Subject",
                    metrics={
                        METRIC_ID: dict(
                            name="Metric", type="type", sources={SOURCE_ID: dict(name="Source", type="type")})})})
        self.database = Mock()
        self.database.reports.find_one.return_value = self.report
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="id", sources=dict(type=dict(name="Type"), new_type=dict(parameters=dict())))

    def test_name(self, request):
        """Test that the source name can be changed."""
        request.json = dict(name="New source name")
        self.assertEqual(dict(ok=True), post_source_attribute(REPORT_ID, SOURCE_ID, "name", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID, source_uuid=SOURCE_ID,
                 description="Jenny changed the name of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from 'Source' to 'New source name'."),
            self.report["delta"])

    def test_post_source_type(self, request):
        """Test that the source type can be changed."""
        request.json = dict(type="new_type")
        self.assertEqual(dict(ok=True), post_source_attribute(REPORT_ID, SOURCE_ID, "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID, source_uuid=SOURCE_ID,
                 description="Jenny changed the type of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from 'type' to 'new_type'."),
            self.report["delta"])


@patch("bottle.request")
class PostSourceParameterTest(unittest.TestCase):
    """Unit tests for the post source parameter route."""

    STATUS_CODE = 200
    STATUS_CODE_REASON = "OK"

    def setUp(self):
        self.url = "https://url"
        self.sources = {SOURCE_ID: dict(name="Source", type="type", parameters=dict())}
        self.report = dict(
            _id=REPORT_ID, title="Report",
            subjects={
                SUBJECT_ID: dict(
                    name="Subject",
                    metrics={
                        METRIC_ID: dict(
                            name="Metric", type="type", sources=self.sources)})})
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.reports.find_one.return_value = self.report
        self.datamodel = dict(
            _id="id",
            sources=dict(
                type=dict(
                    parameters=dict(
                        url=dict(type="url"), username=dict(type="string"), password=dict(type="password")))))
        self.database.datamodels.find_one.return_value = self.datamodel
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
        response = post_source_parameter(REPORT_ID, SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_called_once_with(self.url, auth=None)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID, source_uuid=SOURCE_ID,
                 description="Jenny changed the url of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             f"report 'Report' from '' to '{self.url}'."),
            self.report["delta"])

    @patch.object(requests, 'get')
    def test_url_http_error(self, mock_get, request):
        """Test that the error is reported if a request exception occurs, while checking connection of a url."""
        mock_get.side_effect = requests.exceptions.RequestException
        request.json = dict(url=self.url)
        response = post_source_parameter(REPORT_ID, SOURCE_ID, "url", self.database)
        self.assert_url_check(response, -1, "Unknown error")
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID, source_uuid=SOURCE_ID,
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
        response = post_source_parameter(REPORT_ID, SOURCE_ID, "url", self.database)
        self.assert_url_check(response)
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_called_once_with(self.url, auth=('un', 'pwd'))

    @patch.object(requests, 'get')
    def test_url_no_url_type(self, mock_get, request):
        """Test that the source url can be changed and that the availability is not checked if it's not a url type."""
        self.datamodel["sources"]["type"]["parameters"]["url"]["type"] = "string"
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url="unimportant")
        response = post_source_parameter(REPORT_ID, SOURCE_ID, "url", self.database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert.assert_called_once_with(self.report)
        mock_get.assert_not_called()

    def test_empty_url(self, request):
        """Test that the source url availability is not checked when the url is empty."""
        request.json = dict(url="")
        response = post_source_parameter(REPORT_ID, SOURCE_ID, "url", self.database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert.assert_called_once_with(self.report)

    @patch.object(requests, 'get')
    def test_url_with_token(self, mock_get, request):
        """Test that the source url can be changed and that the availability is checked."""
        mock_get.return_value = self.url_check_get_response
        request.json = dict(url=self.url)
        self.sources[SOURCE_ID]['parameters']['private_token'] = 'xxx'
        response = post_source_parameter(REPORT_ID, SOURCE_ID, "url", self.database)
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
        response = post_source_parameter(REPORT_ID, SOURCE_ID, "password", self.database)
        self.assert_url_check(response)
        self.database.reports.insert.assert_called_once_with(self.report)

    def test_password(self, request):
        """Test that the password can be changed and is not logged."""
        request.json = dict(url="unimportant", password="secret")
        response = post_source_parameter(REPORT_ID, SOURCE_ID, "password", self.database)
        self.assertEqual(response, dict(ok=True))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID, source_uuid=SOURCE_ID,
                 description="Jenny changed the password of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from '' to '******'."),
            self.report["delta"])


class SourceTest(unittest.TestCase):
    """Unit tests for adding and deleting sources."""

    def setUp(self):
        self.database = Mock()
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.database.datamodels.find_one.return_value = dict(
            _id="",
            metrics=dict(metric_type=dict(name="Metric Type", direction="<", default_source="source_type")),
            sources=dict(source_type=dict(parameters=dict())))
        self.report = dict(
            _id=REPORT_ID, title="Report",
            subjects={
                SUBJECT_ID: dict(
                    name="Subject",
                    metrics={
                        METRIC_ID: dict(
                            name=None, type="metric_type", addition="sum", target="0", near_target="10",
                            debt_target=None, accept_debt=False, tags=[], sources=dict())})})
        self.database.reports.find_one.return_value = self.report

    def test_add_source(self):
        """Test that a new source is added."""
        self.assertEqual(dict(ok=True), post_source_new(REPORT_ID, METRIC_ID, self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="Jenny added a new source to metric 'Metric Type' of subject 'Subject' in report "
                             "'Report'."),
            self.report["delta"])

    def test_copy_source(self):
        """Test that a source can be copied."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID] = dict(name="Source")
        self.assertEqual(dict(ok=True), post_source_copy(REPORT_ID, SOURCE_ID, self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="Jenny copied the source 'Source' of metric 'Metric Type' of subject 'Subject' in report "
                             "'Report'."),
            self.report["delta"])

    def test_delete_source(self):
        """Test that the source can be deleted."""
        self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID] = dict(name="Source")
        self.assertEqual(dict(ok=True), delete_source(REPORT_ID, SOURCE_ID, self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(report_uuid=REPORT_ID, subject_uuid=SUBJECT_ID, metric_uuid=METRIC_ID,
                 description="Jenny deleted the source 'Source' from metric 'Metric Type' of subject 'Subject' in "
                             "report 'Report'."),
            self.report["delta"])
