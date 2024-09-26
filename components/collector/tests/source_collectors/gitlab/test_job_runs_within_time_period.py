"""Unit tests for the GitLab job runs within time period collector."""

from datetime import datetime, timedelta

from dateutil.tz import tzutc

from .base import GitLabJobsTestCase


class GitLabJobRunsWithinTimePeriodTest(GitLabJobsTestCase):
    """Unit tests for the GitLab job runs within time period collector."""

    LOOKBACK_DAYS = "3"
    METRIC_TYPE = "job_runs_within_time_period"

    _job3_url = "https://gitlab/job3"  # extending gitlab_jobs_json which already includes job 1 and job 2
    _job4_url = "https://gitlab/job4"
    _job5_url = "https://gitlab/job5"

    async def test_job_lookback_days(self):
        """Test that the job lookback_days are verified."""
        just_now = datetime.now(tz=tzutc())
        last_week = just_now - timedelta(weeks=1)

        self.gitlab_jobs_json.extend(
            [
                {
                    "id": "3",
                    "status": "failed",
                    "name": "job3",
                    "stage": "stage",
                    "created_at": just_now.isoformat(),
                    "web_url": self._job3_url,
                    "ref": "main",
                },
                {
                    "id": "4",
                    "status": "failed",
                    "name": "job4",
                    "stage": "stage",
                    "created_at": last_week.isoformat(),
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
                "build_date": str(just_now.date()),
                "build_datetime": just_now,
            },
        ]
        self.assert_measurement(response, value="1", entities=expected_entities, landing_url=self.LANDING_URL)

    async def test_jobs_not_deduplicated(self):
        """Test that the job runs are not deduplicated."""
        just_now = datetime.now(tz=tzutc())
        yesterday = just_now - timedelta(days=1)

        self.gitlab_jobs_json.extend(
            [
                {
                    "id": "3",
                    "status": "failed",
                    "name": "job3",
                    "stage": "stage",
                    "created_at": just_now.isoformat(),
                    "web_url": self._job3_url,
                    "ref": "main",
                },
                {
                    "id": "4",
                    "status": "failed",
                    "name": "job3",
                    "stage": "stage",
                    "created_at": yesterday.isoformat(),
                    "web_url": self._job3_url,
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
                "build_date": str(just_now.date()),
                "build_datetime": just_now,
            },
            {
                "key": "4",
                "name": "job3",
                "url": self._job3_url,
                "build_status": "failed",
                "branch": "main",
                "stage": "stage",
                "build_date": str(yesterday.date()),
                "build_datetime": just_now - timedelta(days=1),
            },
        ]
        self.assert_measurement(response, value="2", entities=expected_entities, landing_url=self.LANDING_URL)

    async def test_job_lookback_days_on_edge(self):
        """Test the lookback_days around edge of date cut off."""
        just_now = datetime.now(tz=tzutc())
        just_before_cutoff = just_now - timedelta(days=int(self.LOOKBACK_DAYS), minutes=-10)
        just_after_cutoff = just_now - timedelta(days=int(self.LOOKBACK_DAYS), minutes=10)

        self.gitlab_jobs_json.extend(
            [
                {
                    "id": "3",
                    "status": "failed",
                    "name": "job3",
                    "stage": "stage",
                    "created_at": just_now.isoformat(),
                    "web_url": self._job3_url,
                    "ref": "main",
                },
                {
                    "id": "4",
                    "status": "failed",
                    "name": "job4",
                    "stage": "stage",
                    "created_at": just_before_cutoff.isoformat(),
                    "web_url": self._job4_url,
                    "ref": "main",
                },
                {
                    "id": "5",
                    "status": "failed",
                    "name": "job5",
                    "stage": "stage",
                    "created_at": just_after_cutoff.isoformat(),
                    "web_url": self._job5_url,
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
                "build_date": str(just_now.date()),
                "build_datetime": just_now,
            },
            {
                "key": "4",
                "name": "job4",
                "url": self._job4_url,
                "build_status": "failed",
                "branch": "main",
                "stage": "stage",
                "build_date": str(just_before_cutoff.date()),
                "build_datetime": just_before_cutoff,
            },
        ]
        self.assert_measurement(response, value="2", entities=expected_entities, landing_url=self.LANDING_URL)
