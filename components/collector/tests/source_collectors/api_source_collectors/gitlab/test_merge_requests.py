"""Unit tests for the GitLab merge requests collector."""

from .base import GitLabTestCase


class GitLabMergeRequestsTest(GitLabTestCase):
    """Unit tests for the merge requests metric."""

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.metric = dict(type="merge_requests", sources=self.sources, addition="sum")
        self.landing_url = "https://gitlab/namespace/project/-/merge_requests"
        self.merge_request1 = self.create_merge_request(
            1, created="2017-04-29T08:46:00Z", updated="2017-04-29T09:40:00Z", merged="2018-09-07T11:16:17.520Z"
        )
        self.merge_request2 = self.create_merge_request(2, state="locked", upvotes=2)
        self.merge_request3 = self.create_merge_request(3, upvotes=2)
        self.merge_request4 = self.create_merge_request(4, branch="dev")
        self.entity1 = self.create_entity(
            1, created="2017-04-29T08:46:00Z", updated="2017-04-29T09:40:00Z", merged="2018-09-07T11:16:17.520Z"
        )
        self.entity2 = self.create_entity(2, state="locked", upvotes=2)

    @staticmethod
    def create_merge_request(
        nr: int,
        branch: str = "default",
        state: str = "merged",
        created: str = None,
        updated: str = None,
        merged: str = None,
        upvotes: int = 1,
    ):
        """Create a merge request."""
        return dict(
            id=nr,
            title=f"Merge request {nr}",
            target_branch=branch,
            state=state,
            web_url=f"https://gitlab/mr{nr}",
            created_at=created,
            updated_at=updated,
            merged_at=merged,
            closed_at=None,
            upvotes=upvotes,
            downvotes=0,
        )

    @staticmethod
    def create_entity(
        nr: int, state: str = "merged", created: str = None, updated: str = None, merged: str = None, upvotes: int = 1
    ):
        """Create an entity."""
        return dict(
            key=str(nr),
            title=f"Merge request {nr}",
            target_branch="default",
            state=state,
            url=f"https://gitlab/mr{nr}",
            created=created,
            updated=updated,
            merged=merged,
            closed=None,
            upvotes=str(upvotes),
            downvotes="0",
        )

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.sources["source_id"]["parameters"]["merge_request_state"] = ["opened", "closed", "merged"]
        self.sources["source_id"]["parameters"]["upvotes"] = "2"  # Require at least two upvotes
        self.sources["source_id"]["parameters"]["target_branches_to_include"] = ["default"]
        gitlab_json = [
            self.merge_request1,
            self.merge_request2,  # Excluded because of state
            self.merge_request3,  # Excluded because of upvotes
            self.merge_request4,  # Excluded because of target branch
        ]
        response = await self.collect(self.metric, get_request_json_return_value=gitlab_json)
        self.assert_measurement(response, value="1", total="4", entities=[self.entity1], landing_url=self.landing_url)

    async def test_pagination(self):
        """Test that pagination works."""
        response = await self.collect(
            self.metric,
            get_request_json_side_effect=[[self.merge_request1], [self.merge_request2]],
            get_request_links=dict(next=dict(url="https://gitlab/next_page")),
        )
        self.assert_measurement(
            response, value="2", total="2", entities=[self.entity1, self.entity2], landing_url=self.landing_url
        )
