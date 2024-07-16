"""Unit tests for the GitLab jobs collectors."""

from .base import CommonGitLabJobsTestsMixin, GitLabJobsTestCase


class GitLabUnusedJobsTest(CommonGitLabJobsTestsMixin, GitLabJobsTestCase):
    """Unit tests for the GitLab unused jobs metric."""

    METRIC_TYPE = "unused_jobs"

    async def test_nr_of_unused_jobs(self):
        """Test that the number of unused jobs is returned."""
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="2", entities=self.expected_entities, landing_url=self.LANDING_URL)

    async def test_private_token(self):
        """Test that the private token is used."""
        self.set_source_parameter("private_token", "token")
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(
            response,
            value="2",
            api_url="https://gitlab/api/v4/projects/namespace%2Fproject/jobs?per_page=100",
            landing_url=self.LANDING_URL,
        )
