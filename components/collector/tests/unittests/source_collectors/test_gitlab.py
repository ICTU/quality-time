"""Unit tests for the GitLab source."""

from datetime import datetime, timezone
import unittest
from unittest.mock import Mock, patch

from src.metric_collector import MetricCollector


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
            response = MetricCollector(self.metric).get()
        self.assertEqual([dict(key="id", name="ref", url="http://gitlab/job", build_age=build_age,
                               build_date="2019-03-31", build_status="failed")], response["sources"][0]["entities"])
        self.assertEqual("1", response["sources"][0]["value"])

    def test_nr_of_failed_jobs_without_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        self.mock_response.json.return_value = [
            dict(name="job", url="http://job", status="success")]
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("0", response["sources"][0]["value"])


class GitlabSourceUpToDatenessTest(unittest.TestCase):
    """Unit tests for the source up-to-dateness metric."""

    def test_source_up_to_dateness(self):
        """Test that the age of a file in a repo can be measured."""
        sources = dict(
            source_id=dict(
                type="gitlab",
                parameters=dict(
                    url="http://gitlab/", private_token="token", project="project", file_path="file", branch="branch")))
        metric = dict(type="source_up_to_dateness", sources=sources, addition="sum")
        get_response = Mock()
        get_response.json.return_value = dict(committed_date="2019-01-01T09:06:12+00:00")
        head_response = Mock()
        head_response.headers = {"X-Gitlab-Last-Commit-Id": "commit-sha"}
        with patch("requests.head", return_value=head_response):
            with patch("requests.get", return_value=get_response):
                response = MetricCollector(metric).get()
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
        self.assertEqual("http://gitlab/project/blob/branch/file", response["sources"][0]["landing_url"])


class GitlabUnmergedBranchesTest(unittest.TestCase):
    """Unit tests for the unmerged branches metric."""

    def test_unmerged_branches(self):
        """Test that the number of unmerged branches can be measured."""
        sources = dict(
            source_id=dict(
                type="gitlab",
                parameters=dict(
                    url="http://gitlab/", private_token="token", project="project", inactive_days="7")))
        metric = dict(type="unmerged_branches", sources=sources, addition="sum")
        mock_response = Mock()
        mock_response.json.return_value = [
            dict(name="master", merged=False),
            dict(name="unmerged_branch", merged=False, commit=dict(committed_date="2019-04-02T11:33:04.000+02:00")),
            dict(name="active_unmerged_branch", merged=False,
                 commit=dict(committed_date=datetime.now(timezone.utc).isoformat())),
            dict(name="merged_branch", merged=True)]
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("1", response["sources"][0]["value"])
        expected_age = str((datetime.now(timezone.utc) - datetime(2019, 4, 2, 9, 33, 4, tzinfo=(timezone.utc))).days)
        self.assertEqual(
            [dict(key="unmerged_branch", name="unmerged_branch", commit_age=expected_age, commit_date="2019-04-02")],
            response["sources"][0]["entities"])
