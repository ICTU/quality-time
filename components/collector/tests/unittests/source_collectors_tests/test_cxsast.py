"""Unit tests for the Checkmarx CxSAST source."""

from datetime import datetime, timezone

from requests import HTTPError

from source_collectors.cxsast import CxSASTSecurityWarnings
from .source_collector_test_case import SourceCollectorTestCase


class CxSASTTestCase(SourceCollectorTestCase):
    """Base class for testing CxSAST collectors."""
    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="cxsast",
                parameters=dict(
                    url="https://checkmarx/", username="user", password="pass", project="project")))


class CxSASTSourceUpToDatenessTest(CxSASTTestCase):
    """Unit tests for the source up-to-dateness collector."""
    def setUp(self):
        super().setUp()
        self.metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")

    def test_age(self):
        """Test that the age of the last finished scan is returned."""
        get_json = [
            [dict(name="project", id="id")], [dict(dateAndTime=dict(finishedOn="2019-01-01T09:06:12+00:00"))],
            [dict(name="project", id="id")]]
        post_json = [dict(access_token="token")] * 2
        response = self.collect(
            self.metric, get_request_json_side_effect=get_json, post_request_json_side_effect=post_json)
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.assert_value(str(expected_age), response)
        self.assert_landing_url("https://checkmarx/CxWebClient/projectscans.aspx?id=id", response)

    def test_landing_url_without_response(self):
        """Test that a default landing url is returned when connecting to the source fails."""
        response = self.collect(self.metric, post_request_side_effect=RuntimeError)
        self.assert_landing_url("https://checkmarx", response)


class CxSASTSecurityWarningsTest(CxSASTTestCase):
    """Unit tests for the security warnings collector."""

    def setUp(self):
        super().setUp()
        CxSASTSecurityWarnings.CXSAST_SCAN_REPORTS.clear()
        self.metric = dict(type="security_warnings", sources=self.sources, addition="sum")

    def test_nr_of_warnings_and_report_is_requested(self):
        """Test that the number of security warnings is returned."""
        get_json = [
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(status=dict(value="InProcess")),
            dict(highSeverity=1, mediumSeverity=2, lowSeverity=3, infoSeverity=4),
            [dict(name="project", id="id")]]
        post_json = [dict(access_token="token")] * 2 + [dict(reportId=1)]
        response = self.collect(
            self.metric, get_request_json_side_effect=get_json, post_request_json_side_effect=post_json)
        self.assert_value("10", response)
        self.assert_entities([], response)
        self.assertEqual(1, CxSASTSecurityWarnings.CXSAST_SCAN_REPORTS[1000])
        self.assertEqual(datetime.min, self.collector.next_collection())

    def test_report_finished(self):
        """Test that there are entities when the report is ready."""
        CxSASTSecurityWarnings.CXSAST_SCAN_REPORTS[1000] = 1
        get_json = [
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(status=dict(value="Created")),
            dict(highSeverity=1, mediumSeverity=2, lowSeverity=3, infoSeverity=4),
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(status=dict(value="Created")),
            [dict(name="project", id="id")]]
        post_json = [dict(access_token="token")] * 2
        get_text = """
<CxXMLResults>
    <Query name='Name'>
        <Result NodeId='1' Severity='High' FalsePositive='False' FileName='file' Line='42' Column='2'
                DeepLink='https://deeplink'>
        </Result>
        <Result NodeId='2' Severity='High' FalsePositive='True' FileName='file' Line='44' Column='9'
                DeepLink='https://deeplink'>
        </Result>
    </Query>
</CxXMLResults>"""
        response = self.collect(
            self.metric, get_request_json_side_effect=get_json, post_request_json_side_effect=post_json,
            get_request_text=get_text)
        self.assert_value("10", response)
        self.assert_entities(
            [dict(key="1", location="file:42:2", name="Name", severity="High", url="https://deeplink")],
            response)
        self.assertNotEqual(datetime.min, self.collector.next_collection())

    def test_report_deleted(self):
        """Test that a new report will be requested when a previously created report was deleted on the Checkmarx
        server."""
        CxSASTSecurityWarnings.CXSAST_SCAN_REPORTS[1000] = 1
        get_json = [
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(status=dict(value="Created")),
            dict(highSeverity=1, mediumSeverity=2, lowSeverity=3, infoSeverity=4),
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(status=dict(value="Created"))]
        http_errors = [None, None, None, None, HTTPError(500)]
        post_json = [dict(access_token="token")] * 2
        response = self.collect(
            self.metric, get_request_json_side_effect=get_json, get_request_raise_for_status_side_effect=http_errors,
            post_request_json_side_effect=post_json)
        self.assert_value("10", response)
        self.assert_entities([], response)
        self.assertFalse(1000 in CxSASTSecurityWarnings.CXSAST_SCAN_REPORTS)
