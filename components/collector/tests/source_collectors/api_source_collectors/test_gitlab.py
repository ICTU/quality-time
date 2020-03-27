"""Unit tests for the GitLab source."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GitLabTestCase(SourceCollectorTestCase):
    """Base class for testing GitLab collectors."""
    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="gitlab",
                parameters=dict(
                    url="https://gitlab/", project="namespace/project", file_path="file", branch="branch",
                    inactive_days="7", branches_to_ignore=["ignored_.*"])))
        self.gitlab_jobs_json = [
            dict(id="1", status="failed", name="name", stage="stage", created_at="2019-03-31T19:50:39.927Z",
                 web_url="https://gitlab/job", ref="master")]
        build_age = str((datetime.now(timezone.utc) - datetime(2019, 3, 31, 19, 50, 39, 927, tzinfo=timezone.utc)).days)
        self.expected_entities = [
            dict(
                key="1", name="name", stage="stage", branch="master", url="https://gitlab/job",
                build_age=build_age, build_date="2019-03-31", build_status="failed")]


class GitLabFailedJobsTest(GitLabTestCase):
    """Unit tests for the GitLab failed jobs metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="failed_jobs", sources=self.sources, addition="sum")

    async def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        response = await self.collect(self.metric, get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities)

    async def test_nr_of_failed_jobs_without_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        self.gitlab_jobs_json[0]["status"] = "success"
        response = await self.collect(self.metric, get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_private_token(self):
        """Test that the private token is used."""
        self.sources["source_id"]["parameters"]["private_token"] = "token"
        response = await self.collect(self.metric)
        self.assert_measurement(
            response,
            api_url="https://gitlab/api/v4/projects/namespace%2Fproject/jobs?per_page=100&private_token=token",
            parse_error="Traceback")

    async def test_ignore_previous_runs_of_jobs(self):
        """Test that previous runs of the same job are ignored."""
        self.gitlab_jobs_json.insert(
            0,
            dict(id="2", status="success", name="name", stage="stage", created_at="2019-03-31T19:51:39.927Z",
                 web_url="https://gitlab/jobs/2", ref="master"))
        response = await self.collect(self.metric, get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="0", entities=[])


class GitLabUnusedJobsTest(GitLabTestCase):
    """Unit tests for the GitLab unused jobs metric."""

    async def test_nr_of_unused_jobs(self):
        """Test that the number of unused jobs is returned."""
        metric = dict(type="unused_jobs", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities)


class GitlabSourceUpToDatenessTest(GitLabTestCase):
    """Unit tests for the source up-to-dateness metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        self.commit_json = dict(committed_date="2019-01-01T09:06:12+00:00")
        self.expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.head_response = Mock()
        self.head_response.headers = {"X-Gitlab-Last-Commit-Id": "commit-sha"}

    async def test_source_up_to_dateness_file(self):
        """Test that the age of a file in a repo can be measured."""
        with patch("aiohttp.ClientSession.head", AsyncMock(return_value=self.head_response)):
            response = await self.collect(
                self.metric,
                get_request_json_side_effect=[[], self.commit_json, dict(web_url="https://gitlab.com/project")])
        self.assert_measurement(
            response, value=str(self.expected_age), landing_url="https://gitlab.com/project/blob/branch/file")

    async def test_source_up_to_dateness_folder(self):
        """Test that the age of a folder in a repo can be measured."""
        with patch("aiohttp.ClientSession.head", AsyncMock(side_effect=[self.head_response, self.head_response])):
            response = await self.collect(
                self.metric,
                get_request_json_side_effect=[
                    [dict(type="blob", path="file.txt"), dict(type="tree", path="folder")],
                    [dict(type="blob", path="file.txt")], self.commit_json, self.commit_json,
                    dict(web_url="https://gitlab.com/project")])
        self.assert_measurement(
            response, value=str(self.expected_age), landing_url="https://gitlab.com/project/blob/branch/file")

    async def test_landing_url_on_failure(self):
        """Test that the landing url is the API url when GitLab cannot be reached."""
        response = await self.collect(self.metric, get_request_json_side_effect=[ConnectionError])
        self.assert_measurement(response, landing_url="https://gitlab", connection_error="Traceback")


class GitlabUnmergedBranchesTest(GitLabTestCase):
    """Unit tests for the unmerged branches metric."""

    async def test_unmerged_branches(self):
        """Test that the number of unmerged branches can be measured."""
        metric = dict(type="unmerged_branches", sources=self.sources, addition="sum")
        gitlab_json = [
            dict(name="master", default=True, merged=False),
            dict(name="unmerged_branch", default=False, merged=False,
                 commit=dict(committed_date="2019-04-02T11:33:04.000+02:00")),
            dict(name="ignored_branch", default=False, merged=False,
                 commit=dict(committed_date="2019-04-02T11:33:04.000+02:00")),
            dict(name="active_unmerged_branch", default=False, merged=False,
                 commit=dict(committed_date=datetime.now(timezone.utc).isoformat())),
            dict(name="merged_branch", default=False, merged=True)]
        response = await self.collect(metric, get_request_json_return_value=gitlab_json)
        expected_age = str((datetime.now(timezone.utc) - datetime(2019, 4, 2, 9, 33, 4, tzinfo=timezone.utc)).days)
        expected_entities = [
            dict(key="unmerged_branch", name="unmerged_branch", commit_age=expected_age, commit_date="2019-04-02")]
        self.assert_measurement(
            response, value="1", entities=expected_entities, landing_url="https://gitlab/namespace/project/-/branches")
