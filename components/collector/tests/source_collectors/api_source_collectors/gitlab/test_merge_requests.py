"""Unit tests for the GitLab merge requests collector."""

from .base import GitLabTestCase


class GitLabMergeRequestsTest(GitLabTestCase):
    """Unit tests for the merge requests metric."""

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        metric = dict(type="merge_requests", sources=self.sources, addition="sum")
        gitlab_json = [dict(title="Merge request 1")]
        response = await self.collect(metric, get_request_json_return_value=gitlab_json)
        expected_entities = [dict(title="Merge request 1", key="Merge request 1")]
        self.assert_measurement(
            response,
            value="1",
            entities=expected_entities,
            landing_url="https://gitlab/namespace/project/-/merge_requests",
        )
