"""Unit tests for the source routes."""

import unittest
from unittest.mock import call, Mock, patch

import requests

from routes.source import delete_source, post_move_source, post_source_attribute, post_source_copy, post_source_new, \
    post_source_parameter

from .fixtures import create_report, METRIC_ID, METRIC_ID2, METRIC_ID3, METRIC_ID4, REPORT_ID, REPORT_ID2, SOURCE_ID, \
    SOURCE_ID2, SOURCE_ID3, SOURCE_ID4, SOURCE_ID5, SOURCE_ID6, SOURCE_ID7, SUBJECT_ID, SUBJECT_ID2, SUBJECT_ID3


class SourceTestCase(unittest.TestCase):
    """Common fixtures for the source route unit tests."""
    def setUp(self):
        self.url = "https://url"
        self.database = Mock()
        self.database.measurements.find.return_value = []
        self.database.sessions.find_one.return_value = dict(user="Jenny")
        self.data_model = dict(
            _id="id",
            metrics=dict(metric_type=dict(default_source="source_type")),
            sources=dict(
                source_type=dict(
                    name='Source type',
                    parameters=dict(
                        url=dict(type="url", metrics=["metric_type"], default_value=""),
                        username=dict(type="string", metrics=["metric_type"], default_value=""),
                        password=dict(type="password", metrics=["metric_type"], default_value=""),
                        private_token=dict(type="password", metrics=["metric_type"], default_value=""))),
                new_source_type=dict(parameters=dict())))
        self.sources = {
            SOURCE_ID: dict(name="Source", type="source_type", parameters=dict(username="username")),
            SOURCE_ID2: dict(name="Source 2", type="source_type", parameters=dict(username="username"))}
        self.database.datamodels.find_one.return_value = self.data_model


@patch("bottle.request")
class PostSourceAttributeTest(SourceTestCase):
    """Unit tests for the post source attribute route."""

    def setUp(self):
        super().setUp()
        self.report = dict(
            _id=REPORT_ID, title="Report", report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID: dict(
                    name="Subject",
                    metrics={
                        METRIC_ID: dict(
                            name="Metric", type="metric_type", sources=self.sources)})})
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.reports.find_one.return_value = self.report

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
        request.json = dict(type="new_source_type")
        self.assertEqual(dict(ok=True), post_source_attribute(SOURCE_ID, "type", self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
                 description="Jenny changed the type of source 'Source' of metric 'Metric' of subject 'Subject' in "
                             "report 'Report' from 'source_type' to 'new_source_type'."),
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
class PostSourceParameterTest(SourceTestCase):
    """Unit tests for the post source parameter route."""

    STATUS_CODE = 200
    STATUS_CODE_REASON = "OK"

    def setUp(self):
        super().setUp()
        self.report = dict(
            _id=REPORT_ID, title="Report", report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID: dict(
                    name="Subject",
                    metrics={METRIC_ID: dict(name="Metric", type="metric_type", sources=self.sources)}),
                SUBJECT_ID2: dict(
                    name="Subject 2",
                    metrics={METRIC_ID2: dict(name="Metric 2", type="metric_type", sources={})})})
        self.database.reports.distinct.return_value = [REPORT_ID]
        self.database.reports.find_one.return_value = self.report
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
        self.data_model["sources"]["source_type"]["parameters"]["url"]["type"] = "string"
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
        self.data_model["sources"]["source_type"]["parameters"]["url"]["validate_on"] = "password"
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


@patch("bottle.request")
class PostSourceParameterMassEditTest(SourceTestCase):
    """Unit tests for the mass edit variants of the post source parameter route."""

    UNCHANGED_VALUE = "different username"
    OLD_VALUE = "username"
    NEW_VALUE = "new username"

    def setUp(self):
        super().setUp()
        self.sources[SOURCE_ID3] = dict(
            name="Source 3", type="source_type", parameters=dict(username=self.UNCHANGED_VALUE))
        self.sources[SOURCE_ID4] = dict(
            name="Source 4", type="different_type", parameters=dict(username=self.OLD_VALUE))
        self.sources2 = {
            SOURCE_ID5: dict(name="Source 5", type="source_type", parameters=dict(username=self.OLD_VALUE))}
        self.sources3 = {
            SOURCE_ID6: dict(name="Source 6", type="source_type", parameters=dict(username=self.OLD_VALUE))}
        self.sources4 = {
            SOURCE_ID7: dict(name="Source 7", type="source_type", parameters=dict(username=self.OLD_VALUE))}
        self.report = dict(
            _id=REPORT_ID, title="Report", report_uuid=REPORT_ID,
            subjects={
                SUBJECT_ID: dict(
                    name="Subject",
                    metrics={
                        METRIC_ID: dict(name="Metric", type="metric_type", sources=self.sources),
                        METRIC_ID2: dict(name="Metric 2", type="metric_type", sources=self.sources2)}),
                SUBJECT_ID2: dict(
                    name="Subject 2",
                    metrics={METRIC_ID3: dict(name="Metric 3", type="metric_type", sources=self.sources3)})})
        self.report2 = dict(
            _id=REPORT_ID2, title="Report 2", report_uuid=REPORT_ID2,
            subjects={
                SUBJECT_ID3: dict(
                    name="Subject 3",
                    metrics={
                        METRIC_ID4: dict(name="Metric 4", type="metric_type", sources=self.sources4)})})
        self.database.reports.distinct.return_value = [REPORT_ID, REPORT_ID2]
        self.database.reports.find_one.side_effect = [self.report, self.report2]

    def assert_value(self, value_sources_mapping):
        """Assert that the parameters have the correct value."""
        for value, sources in value_sources_mapping.items():
            for source in sources:
                self.assertEqual(value, source["parameters"]["username"])

    def test_mass_edit_reports(self, request):
        """Test that a source parameter can be mass edited."""
        request.json = dict(username=self.NEW_VALUE, edit_scope="reports")
        response = post_source_parameter(SOURCE_ID, "username", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert.assert_has_calls([call(self.report), call(self.report2)])
        self.assert_value({
            self.NEW_VALUE: [
                self.sources[SOURCE_ID], self.sources[SOURCE_ID2], self.sources2[SOURCE_ID5],
                self.sources3[SOURCE_ID6], self.sources4[SOURCE_ID7]],
            self.OLD_VALUE: [self.sources[SOURCE_ID4]],
            self.UNCHANGED_VALUE: [self.sources[SOURCE_ID3]]})
        self.assertEqual(
            dict(
                uuids=[
                    REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID, SOURCE_ID2, METRIC_ID2, SOURCE_ID5, SUBJECT_ID2,
                    METRIC_ID3, SOURCE_ID6, REPORT_ID2, SUBJECT_ID3, METRIC_ID4, SOURCE_ID7],
                description="Jenny changed the username of all sources of type 'Source type' with username 'username' "
                            "in all reports from 'username' to 'new username'."),
            self.report["delta"])

    def test_mass_edit_report(self, request):
        """Test that a source parameter can be mass edited."""
        request.json = dict(username=self.NEW_VALUE, edit_scope="report")
        response = post_source_parameter(SOURCE_ID, "username", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assert_value({
            self.NEW_VALUE: [
                self.sources[SOURCE_ID], self.sources[SOURCE_ID2], self.sources2[SOURCE_ID5],
                self.sources3[SOURCE_ID6]],
            self.OLD_VALUE: [self.sources[SOURCE_ID4]],
            self.UNCHANGED_VALUE: [self.sources[SOURCE_ID3]]})
        self.assertEqual(
            dict(
                uuids=[
                    REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID, SOURCE_ID2, METRIC_ID2, SOURCE_ID5, SUBJECT_ID2,
                    METRIC_ID3, SOURCE_ID6],
                description="Jenny changed the username of all sources of type 'Source type' with username 'username' "
                            "in report 'Report' from 'username' to 'new username'."),
            self.report["delta"])

    def test_mass_edit_subject(self, request):
        """Test that a source parameter can be mass edited."""
        request.json = dict(username=self.NEW_VALUE, edit_scope="subject")
        response = post_source_parameter(SOURCE_ID, "username", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assert_value({
            self.NEW_VALUE: [self.sources[SOURCE_ID], self.sources[SOURCE_ID2], self.sources2[SOURCE_ID5]],
            self.OLD_VALUE: [self.sources[SOURCE_ID4], self.sources3[SOURCE_ID6]],
            self.UNCHANGED_VALUE: [self.sources[SOURCE_ID3]]})
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID, SOURCE_ID2, METRIC_ID2, SOURCE_ID5],
                 description="Jenny changed the username of all sources of type 'Source type' with username 'username' "
                             "of subject 'Subject' in report 'Report' from 'username' to 'new username'."),
            self.report["delta"])

    def test_mass_edit_metric(self, request):
        """Test that a source parameter can be mass edited."""
        request.json = dict(username=self.NEW_VALUE, edit_scope="metric")
        response = post_source_parameter(SOURCE_ID, "username", self.database)
        self.assertEqual(dict(ok=True), response)
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assert_value({
            self.NEW_VALUE: [self.sources[SOURCE_ID], self.sources[SOURCE_ID2]],
            self.OLD_VALUE: [self.sources[SOURCE_ID4], self.sources2[SOURCE_ID5], self.sources3[SOURCE_ID6]],
            self.UNCHANGED_VALUE: [self.sources[SOURCE_ID3]]})
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID, SOURCE_ID2],
                 description="Jenny changed the username of all sources of type 'Source type' with username 'username' "
                             "of metric 'Metric' of subject 'Subject' in report 'Report' from 'username' to "
                             "'new username'."),
            self.report["delta"])


class SourceTest(SourceTestCase):
    """Unit tests for adding and deleting sources."""

    def setUp(self):
        super().setUp()
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

    def test_move_source_within_subject(self):
        """Test that a source can be moved to a different metric in the same subject."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        target_metric = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = dict(
            name="Target metric", type="metric_type", sources={})
        self.assertEqual(dict(ok=True), post_move_source(SOURCE_ID, METRIC_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        self.assertEqual((SOURCE_ID, source), next(iter(target_metric["sources"].items())))
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, METRIC_ID2, SOURCE_ID],
                 description="Jenny moved the source 'Source' from metric 'Metric' of subject 'Subject' in report "
                             "'Report' to metric 'Target metric' of subject 'Subject' in report 'Report'."),
            self.report["delta"])

    def test_move_source_within_report(self):
        """Test that a source can be moved to a different metric in the same report."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        target_metric = dict(name="Target metric", type="metric_type", sources={})
        target_subject = dict(name="Target subject", metrics={METRIC_ID2: target_metric})
        self.report["subjects"][SUBJECT_ID2] = target_subject
        self.assertEqual(dict(ok=True), post_move_source(SOURCE_ID, METRIC_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        self.assertEqual((SOURCE_ID, source), next(iter(target_metric["sources"].items())))
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, SUBJECT_ID2, METRIC_ID, METRIC_ID2, SOURCE_ID],
                 description="Jenny moved the source 'Source' from metric 'Metric' of subject 'Subject' in report "
                             "'Report' to metric 'Target metric' of subject 'Target subject' in report 'Report'."),
            self.report["delta"])

    def test_move_source_across_reports(self):
        """Test that a source can be moved to a different metric in a different report."""
        source = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        target_metric = dict(name="Target metric", type="metric_type", sources={})
        target_subject = dict(name="Target subject", metrics={METRIC_ID2: target_metric})
        target_report = dict(
            _id="target_report", title="Target report", report_uuid=REPORT_ID2, subjects={SUBJECT_ID2: target_subject})
        self.database.reports.find_one.side_effect = [self.report, target_report]
        self.assertEqual(dict(ok=True), post_move_source(SOURCE_ID, METRIC_ID2, self.database))
        self.assertEqual({}, self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"])
        self.assertEqual((SOURCE_ID, source), next(iter(target_metric["sources"].items())))
        expected_description = "Jenny moved the source 'Source' from metric 'Metric' of subject 'Subject' in report " \
                               "'Report' to metric 'Target metric' of subject 'Target subject' in report 'Target " \
                               "report'."
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID], description=expected_description),
            self.report["delta"])
        self.assertEqual(
            dict(uuids=[REPORT_ID2, SUBJECT_ID2, METRIC_ID2, SOURCE_ID], description=expected_description),
            target_report["delta"])

    def test_delete_source(self):
        """Test that the source can be deleted."""
        self.assertEqual(dict(ok=True), delete_source(SOURCE_ID, self.database))
        self.database.reports.insert.assert_called_once_with(self.report)
        self.assertEqual(
            dict(uuids=[REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID],
                 description="Jenny deleted the source 'Source' from metric 'Metric' of subject 'Subject' in "
                             "report 'Report'."),
            self.report["delta"])
