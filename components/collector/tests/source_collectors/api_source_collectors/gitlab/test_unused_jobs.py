"""Unit tests for the GitLab jobs collectors."""

from .base import CommonGitLabJobsTestsMixin, GitLabTestCase


class GitLabUnusedJobsTest(CommonGitLabJobsTestsMixin, GitLabTestCase):
    """Unit tests for the GitLab unused jobs metric."""

    METRIC_TYPE = "unused_jobs"

    async def test_nr_of_unused_jobs(self):
        """Test that the number of unused jobs is returned."""
        response = await self.collect(self.metric, get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_private_token(self):
        """Test that the private token is used."""
        self.sources["source_id"]["parameters"]["private_token"] = "token"
        response = await self.collect(self.metric, get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(
            response, value="2", api_url="https://gitlab/api/v4/projects/namespace%2Fproject/jobs?per_page=100"
        )
