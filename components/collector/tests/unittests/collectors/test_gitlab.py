"""Unit tests for the GitLab source."""

from datetime import datetime, timezone
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
        build_age = str((datetime.now(timezone.utc) - datetime(2019, 3, 31, 19, 50, 39, 927, tzinfo=timezone.utc)).days)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(self.metric)
        self.assertEqual([dict(key="id", name="ref", url="http://gitlab/job", build_age=build_age,
                               build_date="2019-03-31", build_status="failed")], response["sources"][0]["entities"])
        self.assertEqual("1", response["sources"][0]["value"])

    def test_nr_of_failed_jobs_without_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        self.mock_response.json.return_value = [
            dict(name="job", url="http://job", status="success")]
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(self.metric)
        self.assertEqual("0", response["sources"][0]["value"])

    def test_source_up_to_dateness(self):
        """Test that the age of a file in a repo can be measured."""
        parameters = self.sources["source_id"]["parameters"]
        parameters["private_token"] = "token"
        parameters["project"] = "project"
        parameters["file_path"] = "file"
        parameters["branch"] = "branch"
        self.metric["type"] = "source_up_to_dateness"
        response = Mock()
        response.headers = {"X-Gitlab-Last-Commit-Id": "commit-sha"}
        self.mock_response.json.return_value = dict(committed_date="2019-01-01T09:06:12+00:00")
        with patch("requests.head", return_value=response):
            with patch("requests.get", return_value=self.mock_response):
                response = collect_measurement(self.metric)
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
        self.assertEqual("http://gitlab/project/blob/branch/file", response["sources"][0]["landing_url"])
