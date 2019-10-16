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
                    url="https://gitlab/", project="project", file_path="file", branch="branch", inactive_days="7")))


class GitLabFailedJobsTest(GitLabTestCase):
    """Unit tests for the GitLab failed jobs metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="failed_jobs", sources=self.sources, addition="sum")

    def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        gitlab_json = [
            dict(id="id", status="failed", created_at="2019-03-31T19:50:39.927Z",
                 web_url="https://gitlab/job", ref="ref")]
        response = self.collect(self.metric, get_request_json_return_value=gitlab_json)
        build_age = str((datetime.now(timezone.utc) - datetime(2019, 3, 31, 19, 50, 39, 927, tzinfo=timezone.utc)).days)
        expected_entities = [
            dict(key="id", name="ref", url="https://gitlab/job", build_age=build_age, build_date="2019-03-31",
                 build_status="failed")]
        self.assert_measurement(response, value="1", entities=expected_entities)

    def test_nr_of_failed_jobs_without_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        gitlab_json = [dict(name="job", url="https://job", status="success")]
        response = self.collect(self.metric, get_request_json_return_value=gitlab_json)
        self.assert_measurement(response, value="0")

    def test_private_token(self):
        """Test that the private token is used."""
        self.sources["source_id"]["parameters"]["private_token"] = "token"
        response = self.collect(self.metric)
        self.assert_measurement(
            response, api_url="https://gitlab/api/v4/projects/project/jobs?per_page=100&private_token=token",
            parse_error="Traceback")


class GitlabSourceUpToDatenessTest(GitLabTestCase):
    """Unit tests for the source up-to-dateness metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        self.commit_json = dict(committed_date="2019-01-01T09:06:12+00:00")
        self.expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.head_response = Mock()
        self.head_response.headers = {"X-Gitlab-Last-Commit-Id": "commit-sha"}

    def test_source_up_to_dateness_file(self):
        """Test that the age of a file in a repo can be measured."""
        with patch("requests.head", return_value=self.head_response):
            response = self.collect(
                self.metric,
                get_request_json_side_effect=[[], self.commit_json, dict(web_url="https://gitlab.com/project")])
        self.assert_measurement(
            response, value=str(self.expected_age), landing_url="https://gitlab.com/project/blob/branch/file")

    def test_source_up_to_dateness_folder(self):
        """Test that the age of a folder in a repo can be measured."""
        with patch("requests.head", side_effect=[self.head_response, self.head_response]):
            response = self.collect(
                self.metric,
                get_request_json_side_effect=[
                    [dict(type="blob", path="file.txt"), dict(type="tree", path="folder")],
                    [dict(type="blob", path="file.txt")], self.commit_json, self.commit_json,
                    dict(web_url="https://gitlab.com/project")])
        self.assert_measurement(
            response, value=str(self.expected_age), landing_url="https://gitlab.com/project/blob/branch/file")


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
        response = self.collect(metric, get_request_json_return_value=gitlab_json)
        expected_age = str((datetime.now(timezone.utc) - datetime(2019, 4, 2, 9, 33, 4, tzinfo=timezone.utc)).days)
        expected_entities = [
            dict(key="unmerged_branch", name="unmerged_branch", commit_age=expected_age, commit_date="2019-04-02")]
        self.assert_measurement(response, value="1", entities=expected_entities)
