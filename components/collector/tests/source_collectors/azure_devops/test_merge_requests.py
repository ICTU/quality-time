"""Unit tests for the Azure DevOps merge requests collector."""

from source_collectors import AzureDevopsMergeRequests

from .base import AzureDevopsTestCase


class AzureDevopsMergeRequestsTest(AzureDevopsTestCase):
    """Unit tests for the merge requests metric."""

    METRIC_TYPE = "merge_requests"

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.repositories = {"value": [{"id": "id", "name": "project"}]}
        self.landing_url = "https://azure_devops/org/project/_git/project/pullrequests"

    @staticmethod
    def create_merge_request(
        number: int,
        status: str = "active",
        vote: int = 0,
        branch: str = "main",
    ) -> dict[str, str | int | list[dict[str, int]]]:
        """Create a merge request fixture."""
        return {
            "pullRequestId": number,
            "title": f"Pull request {number}",
            "targetRefName": f"refs/heads/{branch}",
            "status": status,
            "creationDate": "2021-02-09T17:10:11.0326704Z",
            "reviewers": [{"vote": 10}, {"vote": vote}],
        }

    def create_entity(self, number: int):
        """Create an Azure DevOps merge request entity."""
        return {
            "key": str(number),
            "title": f"Pull request {number}",
            "target_branch": "refs/heads/main",
            "state": "active",
            "url": f"{self.landing_url.rstrip('s')}/{number}",
            "created": "2021-02-09T17:10:11.0326704Z",
            "closed": None,
            "upvotes": "1",
            "downvotes": "0",
        }

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.set_source_parameter("merge_request_state", ["active"])
        self.set_source_parameter("upvotes", "2")  # Require at least two upvotes
        self.set_source_parameter("target_branches_to_include", ["refs/heads/main"])
        azure_devops_json = [
            {
                "value": [
                    self.create_merge_request(1),
                    self.create_merge_request(2, status="abandoned"),
                    self.create_merge_request(3, vote=10),
                    self.create_merge_request(4, branch="dev"),
                ],
            },
        ]
        response = await self.collect(get_request_json_side_effect=[self.repositories] + 3 * azure_devops_json)
        self.assert_measurement(
            response,
            value="1",
            total="4",
            entities=[self.create_entity(1)],
            landing_url=self.landing_url,
        )

    async def test_pagination(self):
        """Test that pagination works."""
        AzureDevopsMergeRequests.PAGE_SIZE = 1
        azure_devops_json = [
            {"value": [self.create_merge_request(1)]},
            {"value": [self.create_merge_request(2)]},
            {"value": []},
        ]
        response = await self.collect(get_request_json_side_effect=[self.repositories] + 3 * azure_devops_json)
        self.assert_measurement(
            response,
            value="2",
            total="2",
            entities=[self.create_entity(1), self.create_entity(2)],
            landing_url=self.landing_url,
        )
