"""Unit tests for the Azure DevOps Server change failure rate collector."""

from copy import deepcopy
from unittest.mock import DEFAULT as STOP_SENTINEL
from unittest.mock import AsyncMock, PropertyMock, patch

import aiohttp

from base_collectors import MetricCollector

from .base import AzureDevopsPipelinesTestCase

ISSUE_DATE_FIELD = "System.CreatedDate"


class AzureDevopsChangeFailureRateTest(AzureDevopsPipelinesTestCase):
    """Unit tests for the Azure DevOps Server change failure rate collector."""

    METRIC_TYPE = "change_failure_rate"

    def setUp(self):
        """Extend to add Azure DevOps change failure rate fixtures."""
        super().setUp()
        self.set_source_parameter("lookback_days_issues", "424242")
        self.set_source_parameter("lookback_days_pipeline_runs", "424242")

        self.work_item1 = deepcopy(self.work_item)
        self.work_item1["id"] = "id1"
        self.work_item1["fields"][ISSUE_DATE_FIELD] = "2019-10-15 12:25:00+00:00"

        self.work_item2 = deepcopy(self.work_item)
        self.work_item2["id"] = "id2"
        self.work_item2["fields"][ISSUE_DATE_FIELD] = "2019-10-15 12:35:00+00:00"

        for entity_dict in self.expected_entities:
            entity_dict.update({"failed": True})

        self.get_json_side_effects = [
            self.pipelines,
            self.pipeline_runs,
            {"value": []},
            {"value": []},
            self.pipeline_runs,  # needed to parse deployments
            {"value": []},
            {"value": []},
            {"value": []},
            {"value": []},
            {"value": []},
            {"value": []},
        ]
        self.post_json_side_effects = [
            {"workItems": [{"id": "id1"}, {"id": "id2"}]},
            {"value": [self.work_item1, self.work_item2]},  # needed to match with the reported workItems
            {"value": []},
            {"value": [self.work_item1, self.work_item2]},  # needed to parse workItems and mark failed deployments
            self.pipeline_runs,  # needed to mark failed deployments
        ]

    async def collect(
        self,
        *,
        get_request_json_side_effect=None,
        post_request_json_side_effect=None,
        response_url_mock=False,
    ):
        """Allow for mocking aiohttp.ClientResponse.url."""
        get_response = AsyncMock()
        get_response.json = AsyncMock(side_effect=get_request_json_side_effect)

        post_response = AsyncMock()
        post_json_return_value = post_request_json_side_effect[-1]
        post_request_json_side_effect.append(STOP_SENTINEL)
        post_response.json = AsyncMock(return_value=post_json_return_value, side_effect=post_request_json_side_effect)

        if response_url_mock:
            # this is the object within collector_utilities.type.Response.url, which cannot be patched directly
            # because it uses reify to turn the yarl.URL (which contains the property .name) into a cached property
            response_url_mock = AsyncMock()
            url_name_prop_mock = PropertyMock(
                side_effect=[
                    "wiql",  # first call, for AzureDevopsIssues ids
                    "workitemsbatch",  # skip the eq wiql check
                    "workitemsbatch",  # match the actual check
                    "",  # skip the eq wiql check
                    "",  # skip the eq workitemsbatch check
                ]
                * 10
            )
            type(response_url_mock).name = url_name_prop_mock
            post_response.url = response_url_mock

        get_mock = AsyncMock(return_value=get_response)
        post_mock = AsyncMock(return_value=post_response)
        with patch("aiohttp.ClientSession.get", get_mock), patch("aiohttp.ClientSession.post", post_mock):
            async with aiohttp.ClientSession() as session:
                return await MetricCollector(session, self.metric).collect()

    async def test_collect(self):
        """Smoke test for modified collect in test class."""
        response = await self.collect(
            get_request_json_side_effect=[
                {"value": []},
                self.pipeline_runs,  # needed for SourceResponses api_url
                {"value": []},
                {"value": []},
                {"value": []},
                {"value": []},
                {"value": []},
                {"value": []},
                {"value": []},
                {"value": []},
                {"value": []},  # these are all needed for repeated calls to .json()
            ],
            post_request_json_side_effect=[
                {"value": []},
                {"value": []},
                {"value": []},  # these are all needed for repeated calls to .json()
            ],
        )
        self.assert_measurement(response, value="0", entities=[])

    async def test_returns_entities(self):
        """Ensure that entities are returned."""
        response = await self.collect(
            get_request_json_side_effect=self.get_json_side_effects,
            post_request_json_side_effect=self.post_json_side_effects,
            response_url_mock=True,
        )
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_match_issues_after_entities(self):
        """Ensure that only entities followed by an issue are returned."""
        self.work_item1["fields"][ISSUE_DATE_FIELD] = "2019-11-15 12:25:00+00:00"
        response = await self.collect(
            get_request_json_side_effect=self.get_json_side_effects,
            post_request_json_side_effect=self.post_json_side_effects,
            response_url_mock=True,
        )
        self.assert_measurement(response, value="1", entities=self.expected_entities[-1:])

    async def test_dont_match_issues_before_entities(self):
        """Ensure that entities preceded by issues aren't returned."""
        self.work_item1["fields"][ISSUE_DATE_FIELD] = "2019-10-15 12:20:00+00:00"
        self.work_item2["fields"][ISSUE_DATE_FIELD] = "2019-10-15 12:20:00+00:00"
        response = await self.collect(
            get_request_json_side_effect=self.get_json_side_effects,
            post_request_json_side_effect=self.post_json_side_effects,
            response_url_mock=True,
        )
        self.assert_measurement(response, value="0", entities=[])
