"""Unit tests for the GitLab merge requests collector."""

from .base import GitLabTestCase


class GitLabMergeRequestsTest(GitLabTestCase):
    """Unit tests for the merge requests metric."""

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.sources["source_id"]["parameters"]["merge_request_state"] = ["opened", "closed", "merged"]
        metric = dict(type="merge_requests", sources=self.sources, addition="sum")
        gitlab_json = [
            dict(
                id=1,
                title="Merge request 1",
                state="merged",
                web_url="https://gitlab/mr1",
                created_at="2017-04-29T08:46:00Z",
                updated_at="2017-04-29T09:40:00Z",
                merged_at="2018-09-07T11:16:17.520Z",
                closed_at=None,
            ),
            dict(
                id=2,
                title="Merge request 2",
                state="locked",
                web_url="https://gitlab/mr2",
            ),
        ]
        response = await self.collect(metric, get_request_json_return_value=gitlab_json)
        expected_entities = [
            dict(
                title="Merge request 1",
                key="1",
                state="merged",
                url="https://gitlab/mr1",
                created="2017-04-29T08:46:00Z",
                updated="2017-04-29T09:40:00Z",
                merged="2018-09-07T11:16:17.520Z",
                closed=None,
            )
        ]
        self.assert_measurement(
            response,
            value="1",
            entities=expected_entities,
            landing_url="https://gitlab/namespace/project/-/merge_requests",
        )
