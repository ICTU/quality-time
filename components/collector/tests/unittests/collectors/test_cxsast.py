"""Unit tests for the Checkmarx CxSAST source."""

from datetime import datetime, timezone
import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class CxSASTSourceUpToDatenessTest(unittest.TestCase):
    """Unit tests for the source up-to-dateness collector."""
    def test_age(self):
        """Test that the age of the last finished scan is returned."""
        sources = dict(
            source_id=dict(
                type="cxsast",
                parameters=dict(
                    url="http://checkmarx/", username="user", password="pass", project="project")))
        metric = dict(type="source_up_to_dateness", sources=sources, addition="sum")
        get_response = Mock()
        get_response.json.return_value = [dict(dateAndTime=dict(finishedOn="2019-01-01T09:06:12+00:00"))]
        post_response = Mock()
        post_response.json.return_value = dict(access_token="token")
        with patch("requests.post", return_value=post_response):
            with patch("requests.get", return_value=get_response):
                response = collect_measurement(metric)
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
        self.assertEqual(
            "http://checkmarx/CxWebClient/projectscans.aspx?id=project", response["sources"][0]["landing_url"])
