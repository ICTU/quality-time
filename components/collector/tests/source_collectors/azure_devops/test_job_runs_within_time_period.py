"""Unit tests for the Azure DevOps Server pipeline runs within time period collector."""

from .base import AzureDevopsPipelinesTestCase


class AzureDevopsJobRunsWithinTimePeriodTest(AzureDevopsPipelinesTestCase):
    """Unit tests for the Azure DevOps Server pipeline runs within time period collector."""

    METRIC_TYPE = "job_runs_within_time_period"

    async def test_pipeline_runs(self):
        """Test that the pipeline runs are counted."""
        self.set_source_parameter("lookback_days", "424242")

        response = await self.collect(get_request_json_return_value=self.pipeline_runs,
                                      get_request_json_side_effect=[self.pipelines, self.pipeline_runs])

        self.assert_measurement(response, value=str(len(self.expected_entities)), entities=self.expected_entities)
