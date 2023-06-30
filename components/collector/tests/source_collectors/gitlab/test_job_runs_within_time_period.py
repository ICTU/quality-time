"""Unit tests for the GitLab job runs within time period collector."""

from datetime import UTC, datetime, timedelta

from .base import GitLabTestCase


class GitLabJobRunsWithinTimePeriodTest(GitLabTestCase):
    """Unit tests for the GitLab job runs within time period collector."""

    METRIC_TYPE = "job_runs_within_time_period"

    _job3_url = "https://gitlab/job3"  # extending gitlab_jobs_json which already includes job 1 and job 2
    _job4_url = "https://gitlab/job4"

    async def test_job_lookback_days(self):
        """Test that the job lookback_days are verified."""
        self.set_source_parameter("lookback_days", "3")

        now_dt = datetime.now(tz=UTC)
        now_timestamp = now_dt.isoformat()
        last_week_timestamp = (now_dt - timedelta(weeks=1)).isoformat()

        self.gitlab_jobs_json.extend(
            [
                {
                    "id": "3",
                    "status": "failed",
                    "name": "job3",
                    "stage": "stage",
                    "created_at": now_timestamp,
                    "web_url": self._job3_url,
                    "ref": "main",
                },
                {
                    "id": "4",
                    "status": "failed",
                    "name": "job4",
                    "stage": "stage",
                    "created_at": last_week_timestamp,
                    "web_url": self._job4_url,
                    "ref": "main",
                },
            ],
        )

        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        expected_entities = [
            {
                "key": "3",
                "name": "job3",
                "url": self._job3_url,
                "build_status": "failed",
                "branch": "main",
                "stage": "stage",
                "build_date": str(now_dt.date()),
            },
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_jobs_not_deduplicated(self):
        """Test that the job runs are not deduplicated."""
        now_dt = datetime.now(tz=UTC)
        now_timestamp = now_dt.isoformat()
        yesterday_timestamp = (now_dt - timedelta(days=1)).isoformat()

        self.gitlab_jobs_json.extend(
            [
                {
                    "id": "3",
                    "status": "failed",
                    "name": "job3",
                    "stage": "stage",
                    "created_at": now_timestamp,
                    "web_url": self._job3_url,
                    "ref": "main",
                },
                {
                    "id": "4",
                    "status": "failed",
                    "name": "job4",
                    "stage": "stage",
                    "created_at": yesterday_timestamp,
                    "web_url": self._job4_url,
                    "ref": "main",
                },
            ],
        )

        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        expected_entities = [
            {
                "key": "3",
                "name": "job3",
                "url": self._job3_url,
                "build_status": "failed",
                "branch": "main",
                "stage": "stage",
                "build_date": str(now_dt.date()),
            },
            {
                "key": "4",
                "name": "job4",
                "url": self._job4_url,
                "build_status": "failed",
                "branch": "main",
                "stage": "stage",
                "build_date": str((now_dt - timedelta(days=1)).date()),
            },
        ]
        self.assert_measurement(response, value="2", entities=expected_entities)
