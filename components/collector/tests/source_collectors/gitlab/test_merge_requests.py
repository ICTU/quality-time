"""Unit tests for the GitLab merge requests collector."""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp

from base_collectors import MetricCollector

from .base import GitLabTestCase


class GitLabMergeRequestsTest(GitLabTestCase):
    """Unit tests for the merge requests metric."""

    METRIC_TYPE = "merge_requests"
    LANDING_URL = "https://gitlab/namespace/project/-/merge_requests"

    @staticmethod
    def merge_request_json(  # noqa: PLR0913, PLR0917
        number: int,
        branch: str = "default",
        state: str = "merged",
        upvotes: int = 1,
        approved: bool | None = None,
        draft: bool = False,
        auto_merge: bool = False,
    ) -> dict[str, int | str | bool | None]:
        """Create a merge request."""
        return {
            "id": number,
            "title": f"Merge request {number}",
            "targetBranch": branch,
            "state": state,
            "webUrl": f"https://gitlab/mr{number}",
            "createdAt": "2017-04-29T08:46:00Z",
            "updatedAt": "2017-04-29T09:40:00Z",
            "mergedAt": None,
            "upvotes": upvotes,
            "downvotes": 0,
            "approved": approved,
            "draft": draft,
            "autoMergeEnabled": auto_merge,
        }

    @staticmethod
    def merge_requests_json(
        nodes,
        count: int | None = None,
        has_next_page: bool = False,
    ) -> dict[str, dict[str, dict[str, dict[str, dict[str, str | bool] | int]]]]:
        """Create the GraphQL merge request response JSON."""
        return {
            "data": {
                "project": {
                    "mergeRequests": {
                        "pageInfo": {"hasNextPage": has_next_page, "endCursor": "xxx"},
                        "count": len(nodes) if count is None else count,
                        "nodes": nodes,
                    },
                },
            },
        }

    @staticmethod
    def create_entity(
        number: int,
        state: str = "merged",
        upvotes: int = 1,
        approved: str = "?",
        auto_merge: bool = False,
    ) -> dict[str, str | None]:
        """Create an entity."""
        return {
            "key": str(number),
            "title": f"Merge request {number}",
            "target_branch": "default",
            "state": state,
            "approved": approved,
            "url": f"https://gitlab/mr{number}",
            "created": "2017-04-29T08:46:00Z",
            "updated": "2017-04-29T09:40:00Z",
            "merged": None,
            "upvotes": str(upvotes),
            "downvotes": "0",
            "draft": "False",
            "auto_merge": str(auto_merge),
        }

    async def collect_merge_requests(self, *pages, dry_run=None):
        """Collect the merge requests from the GraphQL response pages.

        The collector first does a dry-run to detect the approved field. Unless a separate dry-run response is passed,
        the dry-run gets the first page as response.
        """
        responses = [self.mock_response(page) for page in pages]
        dry_run_response = responses[0] if dry_run is None else self.mock_response(dry_run)
        execute = AsyncMock(side_effect=[dry_run_response, *responses])
        with patch("aiogqlc.GraphQLClient.execute", execute):
            async with aiohttp.ClientSession() as session:
                collector = MetricCollector(session, self.metric)
                return await collector.collect()

    @staticmethod
    def mock_response(json_value) -> AsyncMock:
        """Create a mock GraphQL response that returns the given JSON from its json() method."""
        response = AsyncMock()
        response.json = AsyncMock(return_value=json_value)
        # raise_for_status is sync on aiohttp.ClientResponse; override AsyncMock to avoid unawaited coroutines.
        response.raise_for_status = MagicMock()
        return response

    def assert_measurement(self, measurement, **attributes) -> None:
        """Extend to check the landing URL."""
        super().assert_measurement(measurement, landing_url=self.LANDING_URL, **attributes)

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
            ],
        )
        measurement = await self.collect_merge_requests(merge_requests_json)
        self.assert_measurement(measurement, value="1", total="4", entities=[self.create_entity(1)])

    async def test_pagination(self):
        """Test that pagination works."""
        page1 = self.merge_requests_json([self.merge_request_json(1)], count=2, has_next_page=True)
        page2 = self.merge_requests_json([self.merge_request_json(2)], count=2)
        measurement = await self.collect_merge_requests(page1, page2)
        entities = [self.create_entity(1), self.create_entity(2)]
        self.assert_measurement(measurement, value="2", total="2", entities=entities)

    async def test_approval(self):
        """Test that merge requests can be filtered by approval state."""
        self.set_source_parameter("approval_state", ["approved"])
        merge_requests_json = self.merge_requests_json(
            [self.merge_request_json(1, approved=True), self.merge_request_json(2)],
        )
        measurement = await self.collect_merge_requests(merge_requests_json)
        self.assert_measurement(measurement, value="1", total="2", entities=[self.create_entity(1, approved="yes")])

    async def test_insufficient_permissions(self):
        """Test that the collector returns a helpful error message if no merge request info is returned."""
        measurement = await self.collect_merge_requests({"data": {"project": None}})
        self.assert_measurement(measurement, connection_error="Merge request info for project")

    async def test_ignore_drafts(self):
        """Test that merge requests can be filtered by draft state."""
        self.set_source_parameter("ignore_draft_merge_requests", "yes")
        merge_requests_json = self.merge_requests_json(
            [self.merge_request_json(1, draft=True), self.merge_request_json(2)],
        )
        measurement = await self.collect_merge_requests(merge_requests_json)
        self.assert_measurement(measurement, value="1", total="2", entities=[self.create_entity(2)])

    async def test_ignore_auto_merge(self):
        """Test that merge requests with auto-merge enabled can be ignored, regardless of their number of upvotes."""
        self.set_source_parameter("ignore_merge_requests_with_auto_merge_enabled", "yes")
        self.set_source_parameter("upvotes", "1")
        merge_requests_json = self.merge_requests_json(
            [self.merge_request_json(1, upvotes=0, auto_merge=True), self.merge_request_json(2, upvotes=0)],
        )
        measurement = await self.collect_merge_requests(merge_requests_json)
        self.assert_measurement(measurement, value="1", total="2", entities=[self.create_entity(2, upvotes=0)])

    async def test_do_not_ignore_auto_merge_by_default(self):
        """Test that merge requests with auto-merge enabled are counted by default."""
        merge_requests_json = self.merge_requests_json(
            [self.merge_request_json(1, auto_merge=True), self.merge_request_json(2)],
        )
        measurement = await self.collect_merge_requests(merge_requests_json)
        entities = [self.create_entity(1, auto_merge=True), self.create_entity(2)]
        self.assert_measurement(measurement, value="2", total="2", entities=entities)

    async def test_missing_auto_merge_field(self):
        """Test that a merge request without the auto-merge field is assumed not to have auto-merge enabled."""
        merge_request_json = self.merge_request_json(1)
        del merge_request_json["autoMergeEnabled"]
        measurement = await self.collect_merge_requests(self.merge_requests_json([merge_request_json]))
        self.assert_measurement(measurement, value="1", total="1", entities=[self.create_entity(1)])

    async def test_approved_field_unknown_falls_back(self):
        """Test that the collector falls back to a query without the approved field if GitLab rejects it."""
        unknown_field_json = {"errors": [{"message": "Field 'approved' doesn't exist on type 'MergeRequest'"}]}
        merge_requests_json = self.merge_requests_json([self.merge_request_json(1)])
        measurement = await self.collect_merge_requests(merge_requests_json, dry_run=unknown_field_json)
        self.assert_measurement(measurement, value="1", total="1", entities=[self.create_entity(1)])

    async def test_unrelated_graphql_error_surfaces(self):
        """Test that unrelated GraphQL errors are surfaced as a connection error."""
        measurement = await self.collect_merge_requests({"errors": [{"message": "Something else went wrong"}]})
        self.assert_measurement(measurement, connection_error="Something else went wrong")
