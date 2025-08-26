"""Unit tests for the GitLab CI-pipeline duration collector."""

from datetime import datetime
from unittest.mock import Mock, patch

from dateutil.tz import tzutc

from .base import FakeResponse, GitLabTestCase


class GitLabPipelineDurationTest(GitLabTestCase):
    """Unit tests for the CI-pipeline duration metric."""

    METRIC_TYPE = "pipeline_duration"
    METRIC_ADDITION = "min"
    NOW = datetime(2022, 9, 21, 1, 30, 14, 197, tzinfo=tzutc())
    MOCK_DATETIME = Mock(now=Mock(return_value=NOW))

    def setUp(self) -> None:
        """Extend to set up fixtures."""
        super().setUp()
        self.landing_url = "https://gitlab/project/-/pipelines/1"
        self.pipeline_schedules_json = [{"id": "pipeline schedule id", "description": "pipeline description"}]
        self.scheduled_pipelines_json = [{"id": "pipeline id"}]
        self.pipeline_json = [
            {
                "id": "pipeline id",
                "iid": "iid",
                "project_id": "project id",
                "name": "Pipeline name",
                "created_at": "2022-09-21T01:05:14.197Z",
                "updated_at": "2022-09-21T01:15:14.175Z",
                "ref": "branch",
                "status": "success",
                "source": "push",
                "web_url": self.landing_url,
            },
        ]

    async def collect(self):
        """Override to pass the GitLab pipeline JSON responses."""
        return await super().collect(
            get_request_side_effect=[
                FakeResponse(self.pipeline_schedules_json),  # To fetch all pipeline schedules
                FakeResponse(self.scheduled_pipelines_json),  # To fetch all pipelines for the pipeline schedule
                FakeResponse(self.pipeline_json),  # To fetch all pipelines
            ]
        )

    async def test_duration(self):
        """Test that the duration is returned."""
        response = await self.collect()
        self.assert_measurement(response, value="10", landing_url=self.landing_url)

    @patch("source_collectors.gitlab.json_types.datetime", MOCK_DATETIME)
    async def test_duration_without_updated(self):
        """Test that start and now are used when the pipeline has no updated datetime."""
        del self.pipeline_json[0]["updated_at"]
        response = await self.collect()
        self.assert_measurement(response, value="25", landing_url=self.landing_url)

    async def test_duration_when_no_match(self):
        """Test that an error is returned when no pipelines match."""
        self.set_source_parameter("branches", ["missing"])
        response = await self.collect()
        self.assert_measurement(response, parse_error="No pipelines found within the lookback period")

    async def test_filter_by_pipeline_description(self):
        """Test that pipelines can be filtered by pipeline description."""
        self.set_source_parameter("pipeline_schedules_to_include", ["pipeline description"])
        response = await self.collect()
        self.assert_measurement(response, value="10", landing_url=self.landing_url)
