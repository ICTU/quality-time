"""Unit tests for the GitLab CI-pipeline duration collector."""

from .base import GitLabTestCase


class GitLabPipelineDurationTest(GitLabTestCase):
    """Unit tests for the CI-pipeline duration metric."""

    METRIC_TYPE = "pipeline_duration"
    METRIC_ADDITION = "min"

    def setUp(self):
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
        self.pipeline_detail_json = {
            "id": "pipeline id",
            "iid": "iid",
            "project_id": "project id",
            "created_at": "2022-09-21T01:05:14.197Z",
            "updated_at": "2022-09-21T01:05:50.175Z",
            "duration": 600,
            "ref": "branch",
            "status": "success",
            "source": "push",
            "web_url": self.landing_url,
        }

    async def test_duration(self):
        """Test that the duration is returned."""
        response = await self.collect(
            get_request_json_side_effect=[
                self.pipeline_json,  # To fetch all pipelines
                self.pipeline_detail_json,  # To get the pipeline data for the most recent pipeline
                self.pipeline_detail_json,  # To get the pipeline landing URL for the most recent pipeline
            ]
        )
        self.assert_measurement(response, value="10", landing_url=self.landing_url)

    async def test_duration_when_no_match(self):
        """Test that an error is returned when no pipelines match."""
        self.set_source_parameter("branches", "missing")
        response = await self.collect(get_request_json_return_value=self.pipeline_json)
        self.assert_measurement(response, connection_error="No pipelines found within the lookback period")
