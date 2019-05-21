"""Unit tests for the Checkmarx CxSAST source."""

from datetime import datetime, timezone
import unittest
from unittest.mock import Mock, patch

from src.collector import MetricCollector
from src.collectors.cxsast import CxSASTSecurityWarnings


class CxSASTSourceUpToDatenessTest(unittest.TestCase):
    """Unit tests for the source up-to-dateness collector."""
    def setUp(self):
        sources = dict(
            source_id=dict(
                type="cxsast",
                parameters=dict(
                    url="http://checkmarx/", username="user", password="pass", project="project")))
        self.metric = dict(type="source_up_to_dateness", sources=sources, addition="sum")

    def test_age(self):
        """Test that the age of the last finished scan is returned."""
        get_response = Mock()
        get_response.json.side_effect = [
            [dict(name="project", id="id")], [dict(dateAndTime=dict(finishedOn="2019-01-01T09:06:12+00:00"))],
            [dict(name="project", id="id")]]
        post_response = Mock()
        post_response.json.return_value = dict(access_token="token")
        with patch("requests.post", return_value=post_response):
            with patch("requests.get", return_value=get_response):
                response = MetricCollector(self.metric).get()
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
        self.assertEqual(
            "http://checkmarx/CxWebClient/projectscans.aspx?id=id", response["sources"][0]["landing_url"])

    def test_landing_url_without_response(self):
        """Test that a default landing url is returned when connecting to the source fails."""
        with patch("requests.post", side_effect=RuntimeError):
            response = MetricCollector(self.metric).get()
        self.assertEqual("http://checkmarx", response["sources"][0]["landing_url"])


class CxSASTSecurityWarningsTest(unittest.TestCase):
    """Unit tests for the security warnings collector."""

    def setUp(self):
        CxSASTSecurityWarnings.CXSAST_SCAN_REPORTS.clear()
        sources = dict(
            source_id=dict(
                type="cxsast",
                parameters=dict(
                    url="http://checkmarx/", username="user", password="pass", project="project")))
        self.metric = dict(type="security_warnings", sources=sources, addition="sum")

    def test_nr_of_warnings_and_report_is_requested(self):
        """Test that the number of security warnings is returned."""
        get_response = Mock()
        get_response.json.side_effect = [
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(highSeverity=1, mediumSeverity=2, lowSeverity=3, infoSeverity=4),
            [dict(name="project", id="id")],
            [dict(id=1000)],
            [dict(name="project", id="id")]]
        post_response = Mock()
        post_response.json.side_effect = [
            dict(access_token="token"),
            dict(access_token="token"),
            dict(reportId=1),
            dict(access_token="token")]
        with patch("requests.post", return_value=post_response):
            with patch("requests.get", return_value=get_response):
                collector = MetricCollector(self.metric)
                response = collector.get()
        self.assertEqual("10", response["sources"][0]["value"])
        self.assertEqual([], response["sources"][0]["entities"])
        self.assertEqual(1, CxSASTSecurityWarnings.CXSAST_SCAN_REPORTS[1000])
        self.assertEqual(datetime.min, collector.next_collection())

    def test_report_requested(self):
        """Test that there are no entities while the report hasn't been created yet."""
        CxSASTSecurityWarnings.CXSAST_SCAN_REPORTS[1000] = 1
        get_response = Mock()
        get_response.json.side_effect = [
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(highSeverity=1, mediumSeverity=2, lowSeverity=3, infoSeverity=4),
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(status=dict(value="In Process")),
            [dict(name="project", id="id")]]
        post_response = Mock()
        post_response.json.side_effect = [
            dict(access_token="token"),
            dict(access_token="token"),
            dict(access_token="token")]
        with patch("requests.post", return_value=post_response):
            with patch("requests.get", return_value=get_response):
                collector = MetricCollector(self.metric)
                response = collector.get()
        self.assertEqual("10", response["sources"][0]["value"])
        self.assertEqual([], response["sources"][0]["entities"])
        self.assertEqual(datetime.min, collector.next_collection())

    def test_report_finished(self):
        """Test that there are entities when the report is ready."""
        CxSASTSecurityWarnings.CXSAST_SCAN_REPORTS[1000] = 1
        get_response = Mock()
        get_response.json.side_effect = [
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(highSeverity=1, mediumSeverity=2, lowSeverity=3, infoSeverity=4),
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(status=dict(value="Created")),
            [dict(name="project", id="id")]]
        get_response.text = """
<CxXMLResults>
    <Query name='Name'>
        <Result NodeId='1' Severity='High' FalsePositive='False' FileName='file' Line='42' Column='2'
                DeepLink='http://deeplink'>
        </Result>
        <Result NodeId='2' Severity='High' FalsePositive='True' FileName='file' Line='44' Column='9'
                DeepLink='http://deeplink'>
        </Result>
    </Query>
</CxXMLResults>"""
        post_response = Mock()
        post_response.json.return_value = dict(access_token="token")
        with patch("requests.post", return_value=post_response):
            with patch("requests.get", return_value=get_response):
                collector = MetricCollector(self.metric)
                response = collector.get()
        self.assertEqual("10", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="1", location="file:42:2", name="Name", severity="High", url="http://deeplink")],
            response["sources"][0]["entities"])
        self.assertNotEqual(datetime.min, collector.next_collection())
