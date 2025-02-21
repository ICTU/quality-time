"""Unit tests for the Bitbucket merge requests collector."""

from .base import BitbucketTestCase


class FakeResponse:
    """A fake response class that mimics an async JSON response."""

    def __init__(self, fake_json):
        """Initialize with a fake JSON payload."""
        self.fake_json = fake_json

    async def json(self):
        """Return the fake JSON response asynchronously."""
        return self.fake_json


class BitbucketMergeRequestsTest(BitbucketTestCase):
    """Unit tests for the merge requests metric."""

    METRIC_TYPE = "merge_requests"

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.landing_url = "https://bitbucket/projects/owner/repos/repository/pull-requests"

    @staticmethod
    def create_merge_request(
        number: int,
        approved: bool = False,
        state: str = "OPEN",
        branch: str = "main",
    ) -> dict[str, int | str | list[dict[str, bool]] | dict[str, str]]:
        """Create a merge request fixture."""
        return {
            "id": number,
            "title": f"Pull request {number}",
            "toRef": {"id": f"refs/heads/{branch}"},
            "state": state,
            "createdDate": 1612890611,
            "reviewers": [{"approved": True}, {"approved": approved}],
        }

    def create_entity(self, number: int):
        """Create a Bitbucket merge request entity."""
        return {
            "key": str(number),
            "title": f"Pull request {number}",
            "target_branch": "refs/heads/main",
            "state": "OPEN",
            "url": f"{self.landing_url}/{number}",
            "created": 1612890611,
            "closed": None,
            "upvotes": "1",
            "downvotes": "1",
        }

    def create_mr_json(self, mr, has_next_page: bool = False):
        """Create the JSON for a Bitbucket response."""
        return {
            "size": len(mr),
            "limit": 25,
            "isLastPage": True,
            "start": 0,
            "values": mr,
            "hasNextPage": has_next_page,
        }

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.set_source_parameter("merge_request_state", ["open"])
        self.set_source_parameter("upvotes", "2")  # Require at least two upvotes
        self.set_source_parameter("target_branches_to_include", ["refs/heads/main"])
        bitbucket_json = self.create_mr_json(
            [
                self.create_merge_request(1),
                self.create_merge_request(2, state="DECLINED"),
                self.create_merge_request(3, approved=True),
                self.create_merge_request(4, branch="dev"),
            ]
        )
        response = await self.collect(get_request_json_return_value=bitbucket_json)
        self.assert_measurement(
            response,
            value="1",
            total="4",
            entities=[self.create_entity(1)],
            landing_url=self.landing_url,
        )

    async def test_pagination(self):
        """Test that pagination works."""
        bitbucket_responses = [
            FakeResponse(
                {"size": 1, "isLastPage": False, "nextPageStart": 1, "values": [self.create_merge_request(1)]}
            ),
            FakeResponse(
                {"size": 1, "isLastPage": False, "nextPageStart": 2, "values": [self.create_merge_request(2)]}
            ),
            FakeResponse({"size": 1, "isLastPage": True, "values": [self.create_merge_request(3)]}),
        ]
        response = await self.collect(get_request_side_effect=bitbucket_responses)
        self.assert_measurement(
            response,
            value="3",
            total="3",
            entities=[self.create_entity(1), self.create_entity(2), self.create_entity(3)],
            landing_url=self.landing_url,
        )
