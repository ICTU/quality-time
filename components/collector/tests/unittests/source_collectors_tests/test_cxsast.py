"""Unit tests for the Checkmarx CxSAST source."""

from datetime import datetime, timezone

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

    def test_nr_of_warnings(self):
        """Test that the number of security warnings is returned."""
        metric = dict(type="security_warnings", sources=self.sources, addition="sum")
        get_json = [
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(highSeverity=1, mediumSeverity=2, lowSeverity=3, infoSeverity=4),
            [dict(name="project", id="id")]]
        post_json = [dict(access_token="token")] * 2 + [dict(reportId="1")]
        response = self.collect(metric, get_request_json_side_effect=get_json, post_request_json_side_effect=post_json)
        self.assert_value("10", response)
        self.assert_entities([], response)
