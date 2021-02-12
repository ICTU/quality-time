"""Unit tests for the Azure Devops merge requests collector."""

from source_collectors import AzureDevopsMergeRequests

from .base import AzureDevopsTestCase


class AzureDevopsMergeRequestsTest(AzureDevopsTestCase):
    """Unit tests for the merge requests metric."""

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.metric = dict(type="merge_requests", sources=self.sources, addition="sum")
        self.repositories = dict(value=[dict(id="id", name="project")])
        self.landing_url = "https://azure_devops/org/project/_git/project/pullrequests"

    @staticmethod
    def create_merge_request(number: int, status: str = "active", vote: int = 0, branch: str = "main"):
        """Create a merge request fixture."""
        return dict(
            pullRequestId=number,
            title=f"Pull request {number}",
            targetRefName=f"refs/heads/{branch}",
            status=status,
            creationDate="2021-02-09T17:10:11.0326704Z",
            reviewers=[dict(vote=10), dict(vote=vote)],
        )

    def create_entity(self, number: int):
        """Create an Azure Devops merge request entity."""
        return dict(
            key=str(number),
            title=f"Pull request {number}",
            target_branch="refs/heads/main",
            state="active",
            url=f"{self.landing_url.rstrip('s')}/{number}",
            created="2021-02-09T17:10:11.0326704Z",
            closed=None,
            upvotes="1",
            downvotes="0",
        )

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.sources["source_id"]["parameters"]["merge_request_state"] = ["active"]
        self.sources["source_id"]["parameters"]["upvotes"] = "2"  # Require at least two upvotes
        self.sources["source_id"]["parameters"]["target_branches_to_include"] = ["refs/heads/main"]
        azure_devops_json = dict(
            value=[
                self.create_merge_request(1),
                self.create_merge_request(2, status="abandoned"),
                self.create_merge_request(3, vote=10),
                self.create_merge_request(4, branch="dev"),
            ]
        )
        response = await self.collect(
            self.metric, get_request_json_side_effect=[self.repositories, azure_devops_json, azure_devops_json]
        )
        self.assert_measurement(
            response, value="1", total="4", entities=[self.create_entity(1)], landing_url=self.landing_url
        )

    async def test_pagination(self):
        """Test that pagination works."""
        AzureDevopsMergeRequests.PAGE_SIZE = 1
        azure_devops_json = [
            dict(value=[self.create_merge_request(1)]),
            dict(value=[self.create_merge_request(2)]),
            dict(value=[]),
        ]
        response = await self.collect(
            self.metric, get_request_json_side_effect=[self.repositories] + 2 * azure_devops_json
        )
        self.assert_measurement(
            response,
            value="2",
            total="2",
            entities=[self.create_entity(1), self.create_entity(2)],
            landing_url=self.landing_url,
        )
