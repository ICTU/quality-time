"""Unit tests for the GitLab source."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

from .source_collector_test_case import SourceCollectorTestCase


class GitLabTestCase(SourceCollectorTestCase):
    """Base class for testing GitLab collectors."""
    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="gitlab",
                parameters=dict(
                    url="http://gitlab/", project="project", file_path="file", branch="branch", inactive_days="7")))

    def collect(self, metric, gitlab_json=None):
        gitlab_response = Mock()
        gitlab_response.json.return_value = gitlab_json
        with patch("requests.get", return_value=gitlab_response):
            return super().collect(metric)


class GitLabFailedJobsTest(GitLabTestCase):
    """Unit tests for the GitLab failed jobs metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="failed_jobs", sources=self.sources, addition="sum")

    def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        gitlab_json = [
            dict(id="id", status="failed", created_at="2019-03-31T19:50:39.927Z",
                 web_url="http://gitlab/job", ref="ref")]
        response = self.collect(self.metric, gitlab_json)
        build_age = str((datetime.now(timezone.utc) - datetime(2019, 3, 31, 19, 50, 39, 927, tzinfo=timezone.utc)).days)
        self.assert_entities(
            [dict(key="id", name="ref", url="http://gitlab/job", build_age=build_age, build_date="2019-03-31",
                  build_status="failed")],
            response)
        self.assert_value("1", response)

    def test_nr_of_failed_jobs_without_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        gitlab_json = [dict(name="job", url="http://job", status="success")]
        response = self.collect(self.metric, gitlab_json)
        self.assert_value("0", response)

    def test_private_token(self):
        """Test that the private token is used."""
        self.sources["source_id"]["parameters"]["private_token"] = "token"
        response = self.collect(self.metric)
        self.assert_api_url("http://gitlab/api/v4/projects/project/jobs?per_page=100&private_token=token", response)


class GitlabSourceUpToDatenessTest(GitLabTestCase):
    """Unit tests for the source up-to-dateness metric."""

    def test_source_up_to_dateness(self):
        """Test that the age of a file in a repo can be measured."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        gitlab_json = dict(committed_date="2019-01-01T09:06:12+00:00")
        head_response = Mock()
        head_response.headers = {"X-Gitlab-Last-Commit-Id": "commit-sha"}
        with patch("requests.head", return_value=head_response):
            response = self.collect(metric, gitlab_json)
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.assert_value(str(expected_age), response)
        self.assert_landing_url("http://gitlab/project/blob/branch/file", response)


class GitlabUnmergedBranchesTest(GitLabTestCase):
    """Unit tests for the unmerged branches metric."""

    def test_unmerged_branches(self):
        """Test that the number of unmerged branches can be measured."""
        metric = dict(type="unmerged_branches", sources=self.sources, addition="sum")
        gitlab_json = [
            dict(name="master", merged=False),
            dict(name="unmerged_branch", merged=False, commit=dict(committed_date="2019-04-02T11:33:04.000+02:00")),
            dict(name="active_unmerged_branch", merged=False,
                 commit=dict(committed_date=datetime.now(timezone.utc).isoformat())),
            dict(name="merged_branch", merged=True)]
        response = self.collect(metric, gitlab_json)
        self.assert_value("1", response)
        expected_age = str((datetime.now(timezone.utc) - datetime(2019, 4, 2, 9, 33, 4, tzinfo=timezone.utc)).days)
        self.assert_entities(
            [dict(key="unmerged_branch", name="unmerged_branch", commit_age=expected_age, commit_date="2019-04-02")],
            response)
