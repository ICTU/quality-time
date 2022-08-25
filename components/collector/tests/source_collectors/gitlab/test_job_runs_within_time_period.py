"""Unit tests for the GitLab job runs within time period collector."""

from datetime import datetime, timedelta

from .base import GitLabTestCase


class GitLabJobRunsWithinTimePeriodTest(GitLabTestCase):
    """Unit tests for the GitLab job runs within time period collector."""

    METRIC_TYPE = "job_runs_within_time_period"

    async def test_job_lookback_days(self):
        """Test that the job lookback_days are verified."""
        self.set_source_parameter("lookback_days", "3")

        now_timestamp = datetime.now().isoformat()
        last_week_timestamp = (datetime.now() - timedelta(weeks=1)).isoformat()

        self.gitlab_jobs_json.extend([
            dict(
                id="3",
                status="failed",
                name="job3",
                stage="stage",
                created_at=now_timestamp,
                web_url="https://gitlab/job3",
                ref="master",
            ),
            dict(
                id="4",
                status="failed",
                name="job4",
                stage="stage",
                created_at=last_week_timestamp,
                web_url="https://gitlab/job4",
                ref="master",
            )
        ])

        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        expected_entities = [dict(
            key="3",
            name="job3",
            url="https://gitlab/job3",
            build_status="failed",
            branch="master",
            stage="stage",
            build_date=str(datetime.now().date()),
        )]
        self.assert_measurement(response, value='1', entities=expected_entities)

    async def test_job_without_builds(self):
        """Test that the count is 0 when the job has no builds."""
        response = await self.collect(get_request_json_return_value=[])
        self.assert_measurement(response, value='0', entities=[])

    async def test_jobs_not_deduplicated(self):
        """Test that the job runs are not deduplicated."""
        now_timestamp = datetime.now().isoformat()
        yesterday_timestamp = (datetime.now() - timedelta(days=1)).isoformat()

        self.gitlab_jobs_json.extend([
            dict(
                id="3",
                status="failed",
                name="job3",
                stage="stage",
                created_at=now_timestamp,
                web_url="https://gitlab/job3",
                ref="master",
            ),
            dict(
                id="4",
                status="failed",
                name="job4",
                stage="stage",
                created_at=yesterday_timestamp,
                web_url="https://gitlab/job4",
                ref="master",
            )
        ])

        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        expected_entities = [
            dict(
                key="3",
                name="job3",
                url="https://gitlab/job3",
                build_status="failed",
                branch="master",
                stage="stage",
                build_date=str(datetime.now().date()),
            ),
            dict(
                key="4",
                name="job4",
                url="https://gitlab/job4",
                build_status="failed",
                branch="master",
                stage="stage",
                build_date=str((datetime.now() - timedelta(days=1)).date()),
            )
        ]
        self.assert_measurement(response, value='2', entities=expected_entities)
