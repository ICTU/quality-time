"""Unit tests for the Azure DevOps Server pipeline runs within time period collector."""

from datetime import UTC, datetime, timedelta

from .base import AzureDevopsPipelinesTestCase


class AzureDevopsJobRunsWithinTimePeriodTest(AzureDevopsPipelinesTestCase):
    """Unit tests for the Azure DevOps Server pipeline runs within time period collector."""

    METRIC_TYPE = "job_runs_within_time_period"

    async def test_pipeline_runs(self):
        """Test that the pipeline runs are counted."""
        self.set_source_parameter("lookback_days_pipeline_runs", "424242")

        response = await self.collect(
            get_request_json_return_value=self.pipeline_runs,
            get_request_json_side_effect=[self.pipelines, self.pipeline_runs],
        )

        self.assert_measurement(response, value=str(len(self.expected_entities)), entities=self.expected_entities)

    async def test_pipeline_runs_jobs_exclude(self):
        """Test that the pipeline runs are filtered by name exclude."""
        self.set_source_parameter("lookback_days_pipeline_runs", "424242")
        self.set_source_parameter("jobs_to_ignore", ["azure-pipelines.*"])

        response = await self.collect(
            get_request_json_return_value=self.pipeline_runs,
            get_request_json_side_effect=[self.pipelines, self.pipeline_runs],
        )

        self.assert_measurement(response, value="0", entities=[])

    async def test_pipeline_runs_jobs_empty_include(self):
        """Test that counting pipeline runs filtered by a not-matching name include, works."""
        self.set_source_parameter("lookback_days_pipeline_runs", "424242")
        self.set_source_parameter("jobs_to_include", ["bogus"])

        response = await self.collect(
            get_request_json_return_value=self.pipeline_runs,
            get_request_json_side_effect=[self.pipelines, self.pipeline_runs],
        )

        self.assert_measurement(response, value="0", entities=[])

    async def test_pipeline_runs_lookback_days(self):
        """Test that the pipeline runs are filtered correctly by lookback_days."""
        self.set_source_parameter("lookback_days_pipeline_runs", "3")

        now_dt = datetime.now(tz=UTC)
        now_timestamp = now_dt.isoformat()
        last_week_timestamp = (now_dt - timedelta(weeks=1)).isoformat()

        self.pipeline_runs["value"].extend(
            [
                {
                    "state": "completed",
                    "result": "succeeded",
                    "createdDate": last_week_timestamp,
                    "finishedDate": last_week_timestamp,
                    "pipeline": self.test_pipeline,
                    "id": 5,
                    "name": f"{last_week_timestamp[0:10].replace('-', '')}.1",
                    "url": f"{self.url}/_build/results?buildId=5",
                    "_links": {"web": {"href": f"{self.url}/_build/results?buildId=5"}},
                },
                {
                    "state": "completed",
                    "result": "succeeded",
                    "createdDate": now_timestamp,
                    "finishedDate": now_timestamp,
                    "pipeline": self.test_pipeline,
                    "id": 6,
                    "name": f"{now_timestamp[0:10].replace('-', '')}.1",
                    "url": f"{self.url}/_build/results?buildId=6",
                    "_links": {"web": {"href": f"{self.url}/_build/results?buildId=6"}},
                },
            ],
        )

        response = await self.collect(
            get_request_json_return_value=self.pipeline_runs,
            get_request_json_side_effect=[self.pipelines, self.pipeline_runs],
        )
        now_date_str = now_dt.date().isoformat()
        expected_entities = [
            {
                "name": f"{now_date_str.replace('-', '')}.1",
                "pipeline": self.test_pipeline["name"],
                "key": f"{self.test_pipeline['id']}-{now_date_str.replace('-', '')}_1",  # safe_entity_key
                "url": f"{self.url}/_build/results?buildId=6",
                "build_date": now_date_str,
                "build_status": "completed",
            },
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
