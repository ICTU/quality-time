"""Unit tests for the GitLab merge requests collector."""

from unittest.mock import patch, AsyncMock

from base_collectors import MetricsCollector

from .base import GitLabTestCase


class GitLabMergeRequestsTest(GitLabTestCase):
    """Unit tests for the merge requests metric."""

    METRIC_TYPE = "merge_requests"

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.landing_url = "https://gitlab/namespace/project/-/merge_requests"
        self.collector = MetricsCollector()
        self.collector.data_model = self.data_model

    @staticmethod
    def create_merge_request(
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
    def create_merge_requests(nodes, count: int = None, has_next_page: bool = False):
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
    def create_merge_request_fields(has_approved_field: bool = False):
        """Create the GraphQL merge request fields response JSON."""
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

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.set_source_parameter("merge_request_state", ["opened", "closed", "merged"])
        self.set_source_parameter("upvotes", "2")  # Require at least two upvotes
        self.set_source_parameter("target_branches_to_include", ["default"])
        merge_requests_json = self.create_merge_requests(
            [
                self.create_merge_request(1),
                self.create_merge_request(2, state="locked", upvotes=2),  # Excluded because of state
                self.create_merge_request(3, upvotes=2),  # Excluded because of upvotes
                self.create_merge_request(4, branch="dev"),  # Excluded because of target branch
            ]
        )
        merge_request_fields_response = AsyncMock()
        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_request_fields_response, merge_requests_response])
        merge_request_fields_response.json = AsyncMock(return_value=self.create_merge_request_fields())
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)
        with patch("aiogqlc.GraphQLClient.execute", execute):
            response = await self.collector.collect_sources(None, self.metric)
        entities = [self.create_entity(1)]
        self.assert_measurement(response, value="1", total="4", entities=entities, landing_url=self.landing_url)

    async def test_pagination(self):
        """Test that pagination works."""
        merge_requests_json1 = self.create_merge_requests([self.create_merge_request(1)], count=2, has_next_page=True)
        merge_requests_json2 = self.create_merge_requests([self.create_merge_request(2)], count=2)
        merge_request_fields_response = AsyncMock()
        merge_requests_page1 = AsyncMock()
        merge_requests_page2 = AsyncMock()
        execute = AsyncMock(side_effect=[merge_request_fields_response, merge_requests_page1, merge_requests_page2])
        merge_request_fields_response.json = AsyncMock(return_value=self.create_merge_request_fields())
        merge_requests_page1.json = AsyncMock(return_value=merge_requests_json1)
        merge_requests_page2.json = AsyncMock(return_value=merge_requests_json2)
        with patch("aiogqlc.GraphQLClient.execute", execute):
            response = await self.collector.collect_sources(None, self.metric)
        entities = [self.create_entity(1), self.create_entity(2)]
        self.assert_measurement(response, value="2", total="2", entities=entities, landing_url=self.landing_url)

    async def test_approval(self):
        """Test that merge requests can be filtered by approval state."""
        self.set_source_parameter("approval_state", ["approved"])
        merge_requests_json = self.create_merge_requests(
            [self.create_merge_request(1, approved=True), self.create_merge_request(2)]
        )
        merge_request_fields_response = AsyncMock()
        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_request_fields_response, merge_requests_response])
        merge_request_fields_response.json = AsyncMock(return_value=self.create_merge_request_fields(True))
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)
        with patch("aiogqlc.GraphQLClient.execute", execute):
            response = await self.collector.collect_sources(None, self.metric)
        entities = [self.create_entity(1, approved="yes")]
        self.assert_measurement(response, value="1", total="2", entities=entities, landing_url=self.landing_url)
