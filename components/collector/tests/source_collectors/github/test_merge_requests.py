"""Unit tests for the GitHub merge requests collector."""

from typing import TypedDict
from unittest.mock import AsyncMock, patch

import aiohttp

from base_collectors import MetricCollector

from .base import GitHubTestCase


class TotalCount(TypedDict):
    """The TotalCount JSON as returned by the Github merge request API endpoint."""

    totalCount: str

class Node(TypedDict):
    """The Node JSON as returned by the Github merge request API endpoint."""

    id: int
    title: str
    baseRefName: str
    state: str
    url: str
    createdAt: str
    updatedAt: str
    mergedAt: str
    reviewDecision: str
    reactions: TotalCount
    comments: TotalCount

class PageInfo(TypedDict):
    """The PageInfo JSON as returned by the Github merge request API endpoint."""

    hasNextPage: bool
    endCursor: str

class PullRequests(TypedDict):
    """The PullRequests JSON as returned by the Github merge request API endpoint."""

    pageInfo: PageInfo
    totalCount: int
    nodes: list[Node]

class Repository(TypedDict):
    """The Repository JSON as returned by the Github merge request API endpoint."""

    pullRequests: PullRequests

class Data(TypedDict):
    """The Data JSON as returned by the Github merge request API endpoint."""

    repository: Repository

class Response(TypedDict):
    """The Response JSON as returned by the Github merge request API endpoint."""

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
        review_decision: str | None = None,
    ) -> Node:
        """Create a merge request."""
        return {
            "id": number,
            "title": f"Merge request {number}",
            "baseRefName": branch,
            "state": state,
            "url": f"https://github/pull{number}",
            "createdAt": "2017-04-29T08:46:00Z",
            "updatedAt": "2017-04-29T09:40:00Z",
            "mergedAt": None,
            "reviewDecision": review_decision,
            "reactions": {"totalCount": number},
            "comments": {"totalCount": number},
        }

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

    async def collect_merge_requests(self, execute_mock: AsyncMock):
        """Return the source responses."""
        with patch("aiogqlc.GraphQLClient.execute", execute_mock):
            async with aiohttp.ClientSession() as session:
                collector = MetricCollector(session, self.metric)
                return await collector.collect()

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

        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_requests_response])
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)

        entities = [self.create_entity(1)]
        response = await self.collect_merge_requests(execute)
        self.assert_measurement(
            response,
            value="1",
            total="3",
            entities=entities,
            landing_url=self.LANDING_URL,
        )

    async def test_pagination(self):
        """Test that pagination works."""
        merge_requests_json1 = self.merge_requests_json([self.create_node_json(1)], count=2, has_next_page=True)
        merge_requests_json2 = self.merge_requests_json([self.create_node_json(2)], count=2)
        merge_requests_page1 = AsyncMock()
        merge_requests_page2 = AsyncMock()
        execute = AsyncMock(side_effect=[merge_requests_page1, merge_requests_page2])
        merge_requests_page1.json = AsyncMock(return_value=merge_requests_json1)
        merge_requests_page2.json = AsyncMock(return_value=merge_requests_json2)
        entities = [self.create_entity(1), self.create_entity(2)]
        response = await self.collect_merge_requests(execute)
        self.assert_measurement(
            response,
            value="2",
            total="2",
            entities=entities,
            landing_url=self.LANDING_URL,
        )

    async def test_review_decision(self):
        """Test that merge requests can be filtered by approval state."""
        self.set_source_parameter("review_decision", ["Approved"])
        merge_requests_json = self.merge_requests_json(
            [
                self.create_node_json(1, review_decision="APPROVED"),
                self.create_node_json(2),
            ],
        )
        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_requests_response])
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)
        entities = [self.create_entity(1, review_decision="APPROVED")]
        response = await self.collect_merge_requests(execute)
        self.assert_measurement(
            response,
            value="1",
            total="2",
            entities=entities,
            landing_url=self.LANDING_URL,
        )

    async def test_insufficient_permissions(self):
        """Test that the collector returns a helpful error message if no merge request info is returned."""
        merge_requests_json = {"data": {"repository": None}}
        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_requests_response])
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)
        response = await self.collect_merge_requests(execute)
        self.assert_measurement(
            response,
            landing_url=self.LANDING_URL,
            connection_error="Pull request info for repository",
        )

    async def test_private_token(self):
        """Test that the private token is used."""
        self.set_source_parameter("private_token", "token")
        merge_requests_json = {"data": {"repository": None}}
        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_requests_response])
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)
        response = await self.collect_merge_requests(execute)
        self.assert_measurement(
            response,
            landing_url=self.LANDING_URL,
            connection_error="Pull request info for repository",
        )
