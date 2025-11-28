"""Unit tests for the Azure DevOps Server pipeline duration collector."""

from .base import AzureDevopsPipelinesTestCase


class AzureDevopsPipelineDurationTest(AzureDevopsPipelinesTestCase):
    """Unit tests for the CI-pipeline duration metric."""

    METRIC_TYPE = "pipeline_duration"

    def create_pipeline_run(
        self,
        pipeline_id: int = 1,
        created_at: str = "2019-10-15T12:20:10.1905868Z",
        finished_at: str = "2019-10-15T12:24:10.1905868Z",
        result: str = "succeeded",
    ):
        """Create a pipeline run."""
        self.pipeline_runs["count"] += 1
        self.pipeline_runs["value"].append(
            {
                "state": "completed",
                "result": result,
                "createdDate": created_at,
                "finishedDate": finished_at,
                "pipeline": self.test_pipeline,
                "id": pipeline_id,
                "name": f"20191015.{pipeline_id}",
                "url": f"{self.url}/_build/results?buildId={pipeline_id}",
                "_links": {"web": {"href": f"{self.url}/_build/results?buildId={pipeline_id}"}},
            }
        )

    async def test_report_slowest_duration(self):
        """Test that the duration of the slowest pipeline is returned."""
        self.create_pipeline_run(
            pipeline_id=5, created_at="2025-09-01T00:00:00.0000000Z", finished_at="2025-09-01T00:20:00.0000000Z"
        )
        response = await self.collect(
            get_request_json_return_value=self.pipeline_runs,
            get_request_json_side_effect=[self.pipelines, self.pipeline_runs],
        )
        self.assert_measurement(response, value="20", landing_url=self.url)

    async def test_report_latest_pipeline(self):
        """Test that the duration of the latest pipeline is reported."""
        self.set_source_parameter("pipeline_selection", "latest")
        self.create_pipeline_run(
            pipeline_id=5, created_at="2025-09-01T00:00:00.0000000Z", finished_at="2025-09-01T00:05:00.0000000Z"
        )
        response = await self.collect(
            get_request_json_return_value=self.pipeline_runs,
            get_request_json_side_effect=[self.pipelines, self.pipeline_runs],
        )
        self.assert_measurement(response, value="5", landing_url=self.url)

    async def test_report_average_duration(self):
        """Test that the average duration is reported."""
        self.set_source_parameter("pipeline_selection", "average")
        self.create_pipeline_run(
            pipeline_id=5, created_at="2025-09-01T00:00:00.0000000Z", finished_at="2025-09-01T00:20:00.0000000Z"
        )
        response = await self.collect(
            get_request_json_return_value=self.pipeline_runs,
            get_request_json_side_effect=[self.pipelines, self.pipeline_runs],
        )
        self.assert_measurement(response, value="9", landing_url=self.url)

    async def test_duration_when_no_match(self):
        """Test that an error is returned when no pipelines match."""
        self.set_source_parameter("jobs_to_include", ["missing"])
        response = await self.collect(
            get_request_json_return_value=self.pipeline_runs,
            get_request_json_side_effect=[self.pipelines, self.pipeline_runs],
        )
        self.assert_measurement(response, parse_error="No pipelines found with given job filter(s)")
