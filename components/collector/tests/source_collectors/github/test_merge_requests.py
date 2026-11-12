"""Unit tests for the GitHub merge requests collector."""

from typing import TypedDict
from unittest.mock import AsyncMock, patch

import aiohttp
from aiogqlc import GraphQLClient

from base_collectors import MetricCollector

from .base import GitHubTestCase


class TotalCount(TypedDict):
    """The TotalCount JSON as returned by the GitHub merge request API endpoint."""

    totalCount: str


class Node(TypedDict):
    """The Node JSON as returned by the GitHub merge request API endpoint."""

    id: int
    title: str
    baseRefName: str
    state: str
    url: str
    createdAt: str | None
    updatedAt: str | None
    mergedAt: str | None
    reviewDecision: str
    reactions: TotalCount
    comments: TotalCount


class PageInfo(TypedDict):
    """The PageInfo JSON as returned by the GitHub merge request API endpoint."""

    hasNextPage: bool
    endCursor: str


class PullRequests(TypedDict):
    """The PullRequests JSON as returned by the GitHub merge request API endpoint."""

    pageInfo: PageInfo
    totalCount: int
    nodes: list[Node]


class Repository(TypedDict):
    """The Repository JSON as returned by the GitHub merge request API endpoint."""

    pullRequests: PullRequests


class Data(TypedDict):
    """The Data JSON as returned by the GitHub merge request API endpoint."""

    repository: Repository


class Response(TypedDict):
    """The Response JSON as returned by the GitHub merge request API endpoint."""

    data: Data


class GitHubMergeRequestsTest(GitHubTestCase):
    """Unit tests for the merge request metric."""

    METRIC_TYPE = "merge_requests"
    LANDING_URL = "https://github/owner/repository/pulls"

    @staticmethod
    def create_node_json(
        number: int,
        branch: str = "default",
        state: str = "MERGED",
        review_decision: str = "?",
    ) -> Node:
        """Create a merge request."""
        return Node(
            id=number,
            title=f"Merge request {number}",
            baseRefName=branch,
            state=state,
            url=f"https://github/pull{number}",
            createdAt="2017-04-29T08:46:00Z",
            updatedAt="2017-04-29T09:40:00Z",
            mergedAt=None,
            reviewDecision=review_decision,
            reactions=TotalCount(totalCount=str(number)),
            comments=TotalCount(totalCount=str(number)),
        )

    @staticmethod
    def merge_requests_json(
        nodes,
        count: int | None = None,
        has_next_page: bool = False,
    ) -> Response:
        """Create the GraphQL merge request response JSON."""
        return {
            "data": {
                "repository": {
                    "pullRequests": {
                        "pageInfo": {"hasNextPage": has_next_page, "endCursor": "xxx"},
                        "totalCount": len(nodes) if count is None else count,
                        "nodes": nodes,
                    },
                },
            },
        }

    @staticmethod
    def create_entity(
        number: int,
        state: str = "MERGED",
        review_decision: str = "?",
    ) -> dict[str, str | None]:
        """Create an entity."""
        return {
            "key": str(number),
            "title": f"Merge request {number}",
            "base_ref_name": "default",
            "url": f"https://github/pull{number}",
            "state": state,
            "review_decision": review_decision,
            "created": "2017-04-29T08:46:00Z",
            "updated": "2017-04-29T09:40:00Z",
            "merged": None,
            "comments": str(number),
            "thumbs_up": str(number),
        }

    async def collect_merge_requests(self, *pages):
        """Collect the merge requests from the GraphQL response pages."""
        responses = [AsyncMock(json=AsyncMock(return_value=page)) for page in pages]
        with patch("aiogqlc.GraphQLClient.execute", AsyncMock(side_effect=responses)):
            async with aiohttp.ClientSession() as session:
                collector = MetricCollector(session, self.metric)
                return await collector.collect()

    def assert_measurement(self, measurement, **attributes) -> None:
        """Extend to check the landing URL."""
        super().assert_measurement(measurement, landing_url=self.LANDING_URL, **attributes)

    async def test_merge_requests(self):
        """Test that the number of merge requests can be measured."""
        self.set_source_parameter("merge_request_state", ["Open", "Closed", "Merged"])
        self.set_source_parameter("target_branches_to_include", ["default"])
        merge_requests_json = self.merge_requests_json(
            [
                self.create_node_json(1),
                self.create_node_json(2, state="locked"),  # Excluded because of state
                self.create_node_json(3, branch="dev"),  # Excluded because of target branch
            ],
        )
        measurement = await self.collect_merge_requests(merge_requests_json)
        self.assert_measurement(measurement, value="1", total="3", entities=[self.create_entity(1)])

    async def test_pagination(self):
        """Test that pagination works."""
        page1 = self.merge_requests_json([self.create_node_json(1)], count=2, has_next_page=True)
        page2 = self.merge_requests_json([self.create_node_json(2)], count=2)
        measurement = await self.collect_merge_requests(page1, page2)
        entities = [self.create_entity(1), self.create_entity(2)]
        self.assert_measurement(measurement, value="2", total="2", entities=entities)

    async def test_review_decision(self):
        """Test that merge requests can be filtered by review decision."""
        self.set_source_parameter("review_decision", ["Approved"])
        merge_requests_json = self.merge_requests_json(
            [self.create_node_json(1, review_decision="APPROVED"), self.create_node_json(2)],
        )
        measurement = await self.collect_merge_requests(merge_requests_json)
        entities = [self.create_entity(1, review_decision="APPROVED")]
        self.assert_measurement(measurement, value="1", total="2", entities=entities)

    async def test_insufficient_permissions(self):
        """Test that the collector returns a helpful error message if no merge request info is returned."""
        measurement = await self.collect_merge_requests({"data": {"repository": None}})
        self.assert_measurement(measurement, connection_error="Pull request info for repository")

    async def test_private_token(self):
        """Test that the private token is passed to the GraphQL client as bearer token."""
        self.set_source_parameter("private_token", "token")
        with patch("source_collectors.github.merge_requests.GraphQLClient", wraps=GraphQLClient) as graphql_client:
            measurement = await self.collect_merge_requests(self.merge_requests_json([]))
        self.assertEqual("bearer token", graphql_client.call_args.kwargs["session"].headers["Authorization"])
        self.assert_measurement(measurement, value="0", total="0", entities=[])
