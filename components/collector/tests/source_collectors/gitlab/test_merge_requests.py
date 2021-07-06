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
        self.merge_request1 = self.create_merge_request(1)
        self.merge_request2 = self.create_merge_request(2, state="locked", upvotes=2)
        self.entity1 = self.create_entity(1)
        self.entity2 = self.create_entity(2, state="locked", upvotes=2)
        self.collector = MetricsCollector()
        self.collector.data_model = self.data_model

    @staticmethod
    def create_merge_request(number: int, branch: str = "default", state: str = "merged", upvotes: int = 1):
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
        )

    @staticmethod
    def create_entity(number: int, state: str = "merged", upvotes: int = 1):
        """Create an entity."""
        return dict(
            key=str(number),
            title=f"Merge request {number}",
            target_branch="default",
            state=state,
            approved="?",
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
        merge_request_fields_json = dict(data=dict(__type=dict(fields=[])))  # No approved field
        merge_requests_json = dict(
            data=dict(
                project=dict(
                    mergeRequests=dict(
                        pageInfo=dict(hasNextPage=False),
                        count=4,
                        nodes=[
                            self.merge_request1,
                            self.merge_request2,  # Excluded because of state
                            self.create_merge_request(3, upvotes=2),  # Excluded because of upvotes
                            self.create_merge_request(4, branch="dev"),  # Excluded because of target branch
                        ],
                    )
                )
            )
        )
        merge_request_fields_response = AsyncMock()
        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_request_fields_response, merge_requests_response])
        merge_request_fields_response.json = AsyncMock(return_value=merge_request_fields_json)
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)
        with patch("aiogqlc.GraphQLClient.execute", execute):
            response = await self.collector.collect_sources(None, self.metric)
        self.assert_measurement(response, value="1", total="4", entities=[self.entity1], landing_url=self.landing_url)

    async def test_pagination(self):
        """Test that pagination works."""
        merge_request_fields_json = dict(data=dict(__type=dict(fields=[])))  # No approved field
        merge_requests_json1 = dict(
            data=dict(
                project=dict(
                    mergeRequests=dict(
                        pageInfo=dict(hasNextPage=True, endCursor="xxx"),
                        count=2,
                        nodes=[
                            self.merge_request1,
                        ],
                    )
                )
            )
        )
        merge_requests_json2 = dict(
            data=dict(
                project=dict(
                    mergeRequests=dict(
                        pageInfo=dict(hasNextPage=False),
                        count=2,
                        nodes=[
                            self.merge_request2,
                        ],
                    )
                )
            )
        )
        merge_request_fields_response = AsyncMock()
        merge_requests_response1 = AsyncMock()
        merge_requests_response2 = AsyncMock()
        execute = AsyncMock(
            side_effect=[merge_request_fields_response, merge_requests_response1, merge_requests_response2]
        )
        merge_request_fields_response.json = AsyncMock(return_value=merge_request_fields_json)
        merge_requests_response1.json = AsyncMock(return_value=merge_requests_json1)
        merge_requests_response2.json = AsyncMock(return_value=merge_requests_json2)
        with patch("aiogqlc.GraphQLClient.execute", execute):
            response = await self.collector.collect_sources(None, self.metric)
        self.assert_measurement(
            response, value="2", total="2", entities=[self.entity1, self.entity2], landing_url=self.landing_url
        )

    async def test_approved_field(self):
        """Test that the approved field works."""
        merge_request_fields_json = dict(data=dict(__type=dict(fields=[dict(name="approved")])))
        self.merge_request1["approved"] = True
        merge_requests_json = dict(
            data=dict(
                project=dict(
                    mergeRequests=dict(
                        pageInfo=dict(hasNextPage=False),
                        count=1,
                        nodes=[
                            self.merge_request1,
                        ],
                    )
                )
            )
        )
        merge_request_fields_response = AsyncMock()
        merge_requests_response = AsyncMock()
        execute = AsyncMock(side_effect=[merge_request_fields_response, merge_requests_response])
        merge_request_fields_response.json = AsyncMock(return_value=merge_request_fields_json)
        merge_requests_response.json = AsyncMock(return_value=merge_requests_json)
        with patch("aiogqlc.GraphQLClient.execute", execute):
            response = await self.collector.collect_sources(None, self.metric)
        self.entity1["approved"] = "yes"
        self.assert_measurement(response, value="1", total="1", entities=[self.entity1], landing_url=self.landing_url)
