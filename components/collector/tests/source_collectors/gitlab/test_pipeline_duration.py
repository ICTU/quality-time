"""Unit tests for the GitLab CI-pipeline duration collector."""

from datetime import datetime
from typing import Final
from unittest.mock import Mock, patch

from dateutil.tz import tzutc

from .base import GitLabTestCase


class FakeResponse:
    """Fake GitLab response."""

    links: Final[dict] = {}

    def __init__(self, fake_json) -> None:
        self.fake_json = fake_json

    async def json(self):
        """Return the fake JSON."""
        return self.fake_json


class GitLabPipelineDurationTest(GitLabTestCase):
    """Unit tests for the CI-pipeline duration metric."""

    METRIC_TYPE = "pipeline_duration"
    METRIC_ADDITION = "min"
    NOW = datetime(2022, 9, 22, 1, 30, 14, 197, tzinfo=tzutc())
    MOCK_DATETIME = Mock(now=Mock(return_value=NOW))

    def setUp(self) -> None:
        """Extend to set up fixtures."""
        super().setUp()
        self.landing_url = "https://gitlab/project/-/pipelines/1"
        self.pipeline_json = [
            {
                "id": "pipeline id",
                "iid": "iid",
                "project_id": "project id",
                "created_at": "2022-09-21T01:05:14.197Z",
                "updated_at": "2022-09-21T01:05:50.175Z",
                "ref": "branch",
                "status": "success",
                "source": "push",
                "web_url": self.landing_url,
            },
        ]
        self.pipeline_detail_json: dict[str, str | int] = {
            "id": "pipeline id",
            "iid": "iid",
            "project_id": "project id",
            "created_at": "2022-09-21T01:05:14.197Z",
            "updated_at": "2022-09-21T01:05:50.175Z",
            "ref": "branch",
            "status": "success",
            "source": "push",
            "web_url": self.landing_url,
        }

    async def collect(self):
        """Override to pass the GitLab pipeline JSON responses."""
        return await super().collect(
            get_request_side_effect=[
                FakeResponse(self.pipeline_json),  # To fetch all pipelines
                FakeResponse(self.pipeline_detail_json),  # To get the pipeline details for the most recent pipeline
            ]
        )

    async def test_duration(self):
        """Test that the duration is returned."""
        self.pipeline_detail_json["duration"] = 600
        response = await self.collect()
        self.assert_measurement(response, value="10", landing_url=self.landing_url)

    async def test_duration_without_duration_field(self):
        """Test that start and finish timestamps are used when the pipeline has no duration."""
        self.pipeline_detail_json["started_at"] = "2022-09-21T01:15:14.197Z"
        self.pipeline_detail_json["finished_at"] = "2022-09-21T01:20:14.197Z"
        response = await self.collect()
        self.assert_measurement(response, value="5", landing_url=self.landing_url)

    @patch("source_collectors.gitlab.base.datetime", MOCK_DATETIME)
    async def test_duration_without_duration_and_finished(self):
        """Test that start and now are used when the pipeline has no duration and no finish datetime."""
        self.pipeline_detail_json["started_at"] = "2022-09-22T01:15:14.197Z"
        response = await self.collect()
        self.assert_measurement(response, value="15", landing_url=self.landing_url)

    async def test_duration_without_duration_and_started(self):
        """Test that the created datetime is used if the started datetime is missing, but finished is not."""
        self.pipeline_detail_json["finished_at"] = "2022-09-21T01:08:14.197Z"
        response = await self.collect()
        self.assert_measurement(response, value="3", landing_url=self.landing_url)

    async def test_duration_when_no_match(self):
        """Test that an error is returned when no pipelines match."""
        self.set_source_parameter("branches", "missing")
        response = await self.collect()
        self.assert_measurement(response, connection_error="No pipelines found within the lookback period")
