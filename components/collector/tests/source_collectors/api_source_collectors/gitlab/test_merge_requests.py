"""Unit tests for the GitLab merge requests collector."""

from .base import GitLabTestCase


class GitLabMergeRequestsTest(GitLabTestCase):
    """Unit tests for the merge requests metric."""

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.sources["source_id"]["parameters"]["merge_request_state"] = ["opened", "closed", "merged"]
        self.sources["source_id"]["parameters"]["upvotes"] = "2"  # Require at least two upvotes
        self.sources["source_id"]["parameters"]["target_branches_to_include"] = ["default"]
        metric = dict(type="merge_requests", sources=self.sources, addition="sum")
        gitlab_json = [
            dict(
                id=1,
                title="Merge request 1",
                target_branch="default",
                state="merged",
                web_url="https://gitlab/mr1",
                created_at="2017-04-29T08:46:00Z",
                updated_at="2017-04-29T09:40:00Z",
                merged_at="2018-09-07T11:16:17.520Z",
                closed_at=None,
                upvotes=1,
                downvotes=0,
            ),
            dict(
                id=2,
                title="Merge request 2: excluded because of state",
                state="locked",
                target_branch="default",
                upvotes=1,
                web_url="https://gitlab/mr2",
            ),
            dict(
                id=3,
                title="Merge request 3: excluded because of upvotes",
                state="merged",
                target_branch="default",
                upvotes=2,
                web_url="https://gitlab/mr3",
            ),
            dict(
                id=4,
                title="Merge request 4: excluded because of target branch",
                state="merged",
                web_url="https://gitlab/mr4",
                upvotes=1,
                target_branch="dev",
            ),
        ]
        response = await self.collect(metric, get_request_json_return_value=gitlab_json)
        expected_entities = [
            dict(
                key="1",
                title="Merge request 1",
                target_branch="default",
                state="merged",
                url="https://gitlab/mr1",
                created="2017-04-29T08:46:00Z",
                updated="2017-04-29T09:40:00Z",
                merged="2018-09-07T11:16:17.520Z",
                closed=None,
                upvotes="1",
                downvotes="0",
            )
        ]
        self.assert_measurement(
            response,
            value="1",
            total="4",
            entities=expected_entities,
            landing_url="https://gitlab/namespace/project/-/merge_requests",
        )
