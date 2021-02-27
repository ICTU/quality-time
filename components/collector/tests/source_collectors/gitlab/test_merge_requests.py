"""Unit tests for the GitLab merge requests collector."""

from .base import GitLabTestCase


class GitLabMergeRequestsTest(GitLabTestCase):
    """Unit tests for the merge requests metric."""

    METRIC_TYPE = "merge_requests"

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.landing_url = "https://gitlab/namespace/project/-/merge_requests"
        self.merge_request1 = self.create_merge_request(1)
        self.merge_request2 = self.create_merge_request(2, state="locked", upvotes=2)
        self.entity1 = self.create_entity(1)

    @staticmethod
    def create_merge_request(number: int, branch: str = "default", state: str = "merged", upvotes: int = 1):
        """Create a merge request."""
        return dict(
            id=number,
            title=f"Merge request {number}",
            target_branch=branch,
            state=state,
            web_url=f"https://gitlab/mr{number}",
            created_at="2017-04-29T08:46:00Z",
            updated_at="2017-04-29T09:40:00Z",
            merged_at=None,
            closed_at=None,
            upvotes=upvotes,
            downvotes=0,
        )

    @staticmethod
    def create_entity(number: int, state: str = "merged", upvotes: int = 1):
        """Create an entity."""
        return dict(
            key=str(number),
            title=f"Merge request {number}",
            target_branch="default",
            state=state,
            url=f"https://gitlab/mr{number}",
            created="2017-04-29T08:46:00Z",
            updated="2017-04-29T09:40:00Z",
            merged=None,
            closed=None,
            upvotes=str(upvotes),
            downvotes="0",
        )

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.set_source_parameter("merge_request_state", ["opened", "closed", "merged"])
        self.set_source_parameter("upvotes", "2")  # Require at least two upvotes
        self.set_source_parameter("target_branches_to_include", ["default"])
        gitlab_json = [
            self.merge_request1,
            self.merge_request2,  # Excluded because of state
            self.create_merge_request(3, upvotes=2),  # Excluded because of upvotes
            self.create_merge_request(4, branch="dev"),  # Excluded because of target branch
        ]
        response = await self.collect(get_request_json_return_value=gitlab_json)
        self.assert_measurement(response, value="1", total="4", entities=[self.entity1], landing_url=self.landing_url)

    async def test_pagination(self):
        """Test that pagination works."""
        response = await self.collect(
            get_request_json_side_effect=2 * [[self.merge_request1], [self.merge_request2]],
            get_request_links=dict(next=dict(url="https://gitlab/next_page")),
        )
        entity2 = self.create_entity(2, state="locked", upvotes=2)
        self.assert_measurement(
            response, value="2", total="2", entities=[self.entity1, entity2], landing_url=self.landing_url
        )
