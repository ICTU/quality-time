"""Unit tests for the Azure Devops merge requests collector."""

from .base import AzureDevopsTestCase


class AzureDevopsMergeRequestsTest(AzureDevopsTestCase):
    """Unit tests for the merge requests metric."""

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.metric = dict(type="merge_requests", sources=self.sources, addition="sum")
        self.repositories = dict(value=[dict(id="id", name="project")])

    @staticmethod
    def create_merge_request(number: int, status: str = "active", vote: int = 0, branch: str = "main"):
        """Create a merge request fixture."""
        return dict(
            pullRequestId=number,
            title=f"Pull request {number}",
            targetRefName=f"refs/heads/{branch}",
            status=status,
            url=f"https://azure/pr{number}",
            creationDate="2021-02-09T17:10:11.0326704Z",
            reviewers=[dict(vote=10), dict(vote=vote)],
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
        response = await self.collect(self.metric, get_request_json_side_effect=[self.repositories, azure_devops_json])
        expected_entities = [
            dict(
                key="1",
                title="Pull request 1",
                target_branch="refs/heads/main",
                state="active",
                url="https://azure/pr1",
                created="2021-02-09T17:10:11.0326704Z",
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
            landing_url="https://azure_devops/org/project/_git/project/pullrequests",
        )
