"""Unit tests for the GitLab CI-pipeline duration collector."""

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

from dateutil.tz import tzutc

from .base import FakeResponse, GitLabTestCase

if TYPE_CHECKING:
    from model.measurement import MetricMeasurement


class GitLabPipelineDurationTest(GitLabTestCase):
    """Unit tests for the CI-pipeline duration metric."""

    METRIC_TYPE = "pipeline_duration"
    NOW = datetime(2022, 9, 21, 1, 30, 14, 197, tzinfo=tzutc())
    MOCK_DATETIME = Mock(now=Mock(return_value=NOW))

    def setUp(self) -> None:
        """Extend to set up fixtures."""
        super().setUp()
        self.landing_url = "https://gitlab/project/-/pipelines/1"
        self.pipeline_schedules_json = [{"id": "pipeline schedule id", "description": "pipeline description"}]
        self.scheduled_pipelines_json = [{"id": "pipeline 1"}]
        self.pipeline_json = [self.create_pipeline_run()]
        self.pipeline_details_json = [self.create_pipeline_details()]

    def create_pipeline_run(
        self,
        pipeline_id: str = "1",
        created_at: str = "2022-09-21T01:05:14.197Z",
        updated_at: str = "2022-09-21T01:15:14.175Z",
        status: str = "success",
    ):
        """Create a pipeline run, as returned by the GitLab API to list the pipelines of a project.

        Note that this API does not return the duration of the pipelines; only the API to get one pipeline does.
        """
        return {
            "id": f"pipeline {pipeline_id}",
            "project_id": "project id",
            "name": "Pipeline name",
            "created_at": created_at,
            "updated_at": updated_at,
            "ref": "branch",
            "status": status,
            "source": "push",
            "web_url": self.landing_url,
        }

    def create_pipeline_details(self, pipeline_id: str = "1", duration: int | None = 420, **kwargs):
        """Create the details of a pipeline run, as returned by the GitLab API to get one pipeline.

        The duration is the number of seconds the pipeline ran, excluding the time it spent queued. GitLab does not
        report a duration for pipelines that have not finished, so the duration can be null.
        """
        return self.create_pipeline_run(pipeline_id=pipeline_id, **kwargs) | {
            "started_at": "2022-09-21T01:05:20.000Z",
            "finished_at": "2022-09-21T01:12:20.000Z" if duration else None,
            "duration": duration,
            "queued_duration": 6,
        }

    async def collect(self, **kwargs) -> MetricMeasurement | tuple[MetricMeasurement | None, Mock, Mock] | None:
        """Override to pass the GitLab pipeline JSON responses."""
        responses = [
            FakeResponse(self.pipeline_schedules_json),  # To fetch all pipeline schedules
            FakeResponse(self.scheduled_pipelines_json),  # To fetch all pipelines for the pipeline schedule
            FakeResponse(self.pipeline_json),  # To fetch all pipelines
        ]
        if self.exclude_idle_time():
            # To fetch the details of each pipeline that passes the filters, because only the API to get one pipeline
            # returns the duration of the pipeline
            responses.extend(FakeResponse(details) for details in self.pipeline_details_json)
        return await super().collect(get_request_side_effect=responses, **kwargs)

    def exclude_idle_time(self) -> bool:
        """Return whether idle time is excluded from the pipeline duration."""
        return str(self.sources["source_id"]["parameters"].get("exclude_idle_time_from_pipeline_duration")) == "yes"

    async def test_report_slowest_duration(self):
        """Test that the duration of the slowest pipeline is returned."""
        slowest = self.create_pipeline_run(
            pipeline_id="2", created_at="2025-09-01T00:00:00", updated_at="2025-09-01T00:20:00"
        )
        self.pipeline_json.append(slowest)
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="20", landing_url=self.landing_url)

    async def test_report_latest_pipeline(self):
        """Test that the duration of the latest pipeline is reported."""
        self.set_source_parameter("pipeline_selection", "latest")
        latest = self.create_pipeline_run(
            pipeline_id="2", created_at="2025-09-01T00:00:00", updated_at="2025-09-01T00:05:00"
        )
        self.pipeline_json.append(latest)
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="5", landing_url=self.landing_url)

    async def test_report_average_duration(self):
        """Test that the average duration is reported."""
        self.set_source_parameter("pipeline_selection", "average")
        second = self.create_pipeline_run(
            pipeline_id="2", created_at="2025-09-01T00:00:00", updated_at="2025-09-01T00:20:00"
        )
        self.pipeline_json.append(second)
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="15", landing_url=self.landing_url)

    @patch("source_collectors.gitlab.json_types.datetime", MOCK_DATETIME)
    async def test_duration_without_updated(self):
        """Test that start and now are used when the pipeline has no updated datetime."""
        del self.pipeline_json[0]["updated_at"]
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="25", landing_url=self.landing_url)

    async def test_duration_when_no_match(self):
        """Test that an error is returned when no pipelines match."""
        self.set_source_parameter("branches", ["missing"])
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, parse_error="No pipelines found with given filter(s)")

    async def test_filter_by_pipeline_description(self):
        """Test that pipelines can be filtered by pipeline description."""
        self.set_source_parameter("pipeline_schedules_to_include", ["pipeline description"])
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="10", landing_url=self.landing_url)

    async def test_exclude_idle_time(self):
        """Test that idle time can be excluded from pipeline duration.

        GitLab reports the duration of a pipeline in seconds, so the 420 seconds of the pipeline are reported as
        seven minutes.
        """
        self.set_source_parameter("exclude_idle_time_from_pipeline_duration", "yes")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="7", landing_url=self.landing_url)

    async def test_exclude_idle_time_when_pipeline_has_not_finished(self):
        """Test that pipelines for which GitLab reports no duration are counted as taking zero minutes."""
        self.set_source_parameter("exclude_idle_time_from_pipeline_duration", "yes")
        unfinished = {"pipeline_id": "2", "status": "running"}
        self.pipeline_json.append(self.create_pipeline_run(**unfinished))
        self.pipeline_details_json.append(self.create_pipeline_details(duration=None, **unfinished))
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="7", landing_url=self.landing_url)

    async def test_exclude_idle_time_when_no_match(self):
        """Test that no pipeline details are fetched when no pipelines pass the filters."""
        self.set_source_parameter("exclude_idle_time_from_pipeline_duration", "yes")
        self.set_source_parameter("branches", ["missing"])
        measurement, get, _post = await self.collect_measurement_and_mocks()
        self.assert_measurement(measurement, parse_error="No pipelines found with given filter(s)")
        self.assertEqual([], self.pipeline_detail_urls(get))

    async def test_pipeline_details_fetched_when_excluding_idle_time(self):
        """Test that the details of the pipelines that pass the filters are fetched, to get their duration."""
        self.set_source_parameter("exclude_idle_time_from_pipeline_duration", "yes")
        _measurement, get, _post = await self.collect_measurement_and_mocks()
        expected_url = "https://gitlab/api/v4/projects/namespace%2Fproject/pipelines/pipeline 1?per_page=100"
        self.assertEqual([expected_url], self.pipeline_detail_urls(get))

    async def test_pipeline_details_not_fetched_when_including_idle_time(self):
        """Test that the pipeline details are not fetched when idle time is included in the pipeline duration."""
        measurement, get, _post = await self.collect_measurement_and_mocks()
        self.assert_measurement(measurement, value="10", landing_url=self.landing_url)
        # Only the pipeline schedules, the scheduled pipelines, and the pipelines are fetched
        self.assertEqual(3, len(self.request_urls(get)))
        self.assertEqual([], self.pipeline_detail_urls(get))

    @staticmethod
    def request_urls(get: Mock) -> list[str]:
        """Return the URLs of the get requests."""
        return [str(call.args[0]) for call in get.call_args_list]

    @classmethod
    def pipeline_detail_urls(cls, get: Mock) -> list[str]:
        """Return the URLs of the get requests for the details of individual pipelines."""
        return [url for url in cls.request_urls(get) if "/pipelines/" in url]
