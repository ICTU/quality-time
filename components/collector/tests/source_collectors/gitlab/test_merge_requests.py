"""Unit tests for the GitLab merge requests collector."""

from unittest.mock import patch, AsyncMock

from base_collectors import MetricCollector

from .base import GitLabTestCase


class GitLabMergeRequestsTest(GitLabTestCase):
    """Unit tests for the merge requests metric."""

    METRIC_TYPE = "merge_requests"
    LANDING_URL = "https://gitlab/namespace/project/-/merge_requests"

    @staticmethod
    def merge_request_json(
        number: int, branch: str = "default", state: str = "merged", upvotes: int = 1, approved: bool = None
    ):
        """Create a merge request."""
        return dict(
            id=number,
            title=f"Merge request {number}",
            targetBranch=branch,
            state=state,
            webUrl=f"https://gitlab/mr{number}",
            createdAt="2017-04-29T08:46:00Z",
            updatedAt="2017-04-29T09:40:00Z",
            mergedAt=None,
            upvotes=upvotes,
            downvotes=0,
            approved=approved,
        )

    @staticmethod
    def merge_requests_json(nodes, count: int = None, has_next_page: bool = False):
        """Create the GraphQL merge request response JSON."""
        return dict(
            data=dict(
                project=dict(
                    mergeRequests=dict(
                        pageInfo=dict(hasNextPage=has_next_page, endCursor="xxx"),
                        count=len(nodes) if count is None else count,
                        nodes=nodes,
                    )
                )
            )
        )

    @staticmethod
    def merge_request_fields_json(has_approved_field: bool = False):
        """Return the GraphQL merge request fields response JSON."""
        fields = [dict(name="approved")] if has_approved_field else []
        return dict(data=dict(__type=dict(fields=fields)))

    @staticmethod
    def create_entity(number: int, state: str = "merged", upvotes: int = 1, approved: str = "?"):
        """Create an entity."""
        return dict(
            key=str(number),
            title=f"Merge request {number}",
            target_branch="default",
            state=state,
            approved=approved,
            url=f"https://gitlab/mr{number}",
            created="2017-04-29T08:46:00Z",
            updated="2017-04-29T09:40:00Z",
            merged=None,
            upvotes=str(upvotes),
            downvotes="0",
        )

    async def collect_merge_requests(self, execute_mock):
        """Return the source responses."""
        with patch("aiogqlc.GraphQLClient.execute", execute_mock):
            collector = MetricCollector(None, self.metric, self.data_model)
            return await collector.get()

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.set_source_parameter("merge_request_state", ["opened", "closed", "merged"])
        self.set_source_parameter("upvotes", "2")  # Require at least two upvotes
        self.set_source_parameter("target_branches_to_include", ["default"])
        merge_requests_json = self.merge_requests_json(
            [
                self.merge_request_json(1),
                self.merge_request_json(2, state="locked", upvotes=2),  # Excluded because of state
                self.merge_request_json(3, upvotes=2),  # Excluded because of upvotes
                self.merge_request_json(4, branch="dev"),  # Excluded because of target branch
            ]
        )
        merge_request_fields_response = AsyncMock()
        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_request_fields_response, merge_requests_response])
        merge_request_fields_response.json = AsyncMock(return_value=self.merge_request_fields_json())
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)
        entities = [self.create_entity(1)]
        response = await self.collect_merge_requests(execute)
        self.assert_measurement(response, value="1", total="4", entities=entities, landing_url=self.LANDING_URL)

    async def test_pagination(self):
        """Test that pagination works."""
        merge_requests_json1 = self.merge_requests_json([self.merge_request_json(1)], count=2, has_next_page=True)
        merge_requests_json2 = self.merge_requests_json([self.merge_request_json(2)], count=2)
        merge_request_fields_response = AsyncMock()
        merge_requests_page1 = AsyncMock()
        merge_requests_page2 = AsyncMock()
        execute = AsyncMock(side_effect=[merge_request_fields_response, merge_requests_page1, merge_requests_page2])
        merge_request_fields_response.json = AsyncMock(return_value=self.merge_request_fields_json())
        merge_requests_page1.json = AsyncMock(return_value=merge_requests_json1)
        merge_requests_page2.json = AsyncMock(return_value=merge_requests_json2)
        entities = [self.create_entity(1), self.create_entity(2)]
        response = await self.collect_merge_requests(execute)
        self.assert_measurement(response, value="2", total="2", entities=entities, landing_url=self.LANDING_URL)

    async def test_approval(self):
        """Test that merge requests can be filtered by approval state."""
        self.set_source_parameter("approval_state", ["approved"])
        merge_requests_json = self.merge_requests_json(
            [self.merge_request_json(1, approved=True), self.merge_request_json(2)]
        )
        merge_request_fields_response = AsyncMock()
        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_request_fields_response, merge_requests_response])
        merge_request_fields_response.json = AsyncMock(return_value=self.merge_request_fields_json(True))
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)
        entities = [self.create_entity(1, approved="yes")]
        response = await self.collect_merge_requests(execute)
        self.assert_measurement(response, value="1", total="2", entities=entities, landing_url=self.LANDING_URL)
