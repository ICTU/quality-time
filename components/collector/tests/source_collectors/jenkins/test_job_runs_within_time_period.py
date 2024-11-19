"""Unit tests for the Jenkins job runs within time period collector."""

from datetime import datetime, timedelta

from shared.utils.date_time import now

from .base import JenkinsTestCase


class JenkinsJobRunsWithinTimePeriodTest(JenkinsTestCase):
    """Unit tests for the Jenkins job runs within time period collector."""

    METRIC_TYPE = "job_runs_within_time_period"

    async def test_all_builds(self):
        """Test that all builds are counted if no filtering is done."""
        self.set_source_parameter("lookback_days", "100000")
        jenkins_json = {
            "jobs": [{"name": "job", "url": self.job_url, "buildable": True, "color": "blue", "builds": self.builds}],
        }
        response = await self.collect(get_request_json_return_value=jenkins_json)
        expected_entities = [{"build_count": "2", "key": "job", "name": "job", "url": self.job_url}]
        self.assert_measurement(response, value="2", entities=expected_entities)

    async def test_filter_by_result_type(self):
        """Test that the builds can be filtered by result type."""
        self.set_source_parameter("lookback_days", "100000")
        self.set_source_parameter("result_type", ["Failure"])
        jenkins_json = {
            "jobs": [{"name": "job", "url": self.job_url, "buildable": True, "color": "blue", "builds": self.builds}],
        }
        response = await self.collect(get_request_json_return_value=jenkins_json)
        expected_entities = [{"build_count": "1", "key": "job", "name": "job", "url": self.job_url}]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_job_lookback_days(self):
        """Test that the build lookback_days are verified."""
        self.set_source_parameter("lookback_days", "3")

        now_dt = now()
        now_timestamp = int(datetime.timestamp(now_dt) * 1000)
        last_week_timestamp = int(datetime.timestamp(now_dt - timedelta(weeks=1)) * 1000)
        self.builds.extend(
            [
                {"result": "SUCCESS", "timestamp": now_timestamp},
                {"result": "SUCCESS", "timestamp": last_week_timestamp},
            ],
        )

        jenkins_json = {
            "jobs": [{"name": "job", "url": self.job_url, "buildable": True, "color": "blue", "builds": self.builds}],
        }
        response = await self.collect(get_request_json_return_value=jenkins_json)

        expected_entities = [{"build_count": "1", "key": "job", "name": "job", "url": self.job_url}]
        self.assert_measurement(response, value="1", entities=expected_entities)
