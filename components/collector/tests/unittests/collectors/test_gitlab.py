"""Unit tests for the GitLab source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class GitLabTest(unittest.TestCase):
    """Unit tests for the GitLab metrics."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(
            type="gitlab", parameters=dict(url="http://gitlab/")))
        self.metric = dict(type="failed_jobs", sources=self.sources, addition="sum")

    def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        self.mock_response.json.return_value = [
            dict(id="id", status="failed", created_at="2019-03-31T19:50:39.927Z",
                 web_url="http://gitlab/job", ref="ref")]
        build_age = str((datetime.now() - datetime(2019, 3, 31, 19, 50, 39, 927)).days)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(self.metric)
        self.assertEqual([dict(key="id", name="ref", url="http://gitlab/job", build_age=build_age,
                               build_date="2019-03-31", build_status="failed")], response["sources"][0]["units"])
        self.assertEqual("1", response["sources"][0]["value"])

    def test_nr_of_failed_jobs_with_private_token(self):
        """Test that the number of failed jobs is returned."""
        self.sources["source_id"]["parameters"]["private_token"] = "token"
        self.mock_response.json.return_value = [
            dict(name="job", url="http://job", status="success")]
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(self.metric)
        self.assertEqual("0", response["sources"][0]["value"])
