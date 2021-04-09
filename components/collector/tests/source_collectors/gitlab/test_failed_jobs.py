"""Unit tests for the GitLab jobs collectors."""

from .base import CommonGitLabJobsTestsMixin, GitLabTestCase


class GitLabFailedJobsTest(CommonGitLabJobsTestsMixin, GitLabTestCase):
    """Unit tests for the GitLab failed jobs metric."""

    METRIC_TYPE = "failed_jobs"

    async def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_nr_of_failed_jobs_without_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        for job in self.gitlab_jobs_json:
            job["status"] = "success"
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_ignore_previous_runs_of_jobs(self):
        """Test that previous runs of the same job are ignored."""
        self.gitlab_jobs_json.extend(
            [
                dict(
                    id="3",
                    status="success",
                    name="job1",
                    stage="stage",
                    created_at="2018-03-31T19:41:39.927Z",
                    web_url="https://gitlab/jobs/3",
                    ref="master",
                ),
                dict(
                    id="4",
                    status="success",
                    name="job1",
                    stage="stage",
                    created_at="2020-03-31T19:41:39.927Z",
                    web_url="https://gitlab/jobs/4",
                    ref="master",
                ),
            ]
        )
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities[-1:])

    async def test_private_token(self):
        """Test that the private token is used."""
        self.set_source_parameter("private_token", "token")
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(
            response,
            value="2",
            api_url="https://gitlab/api/v4/projects/namespace%2Fproject/jobs?per_page=100&scope=failed",
        )
