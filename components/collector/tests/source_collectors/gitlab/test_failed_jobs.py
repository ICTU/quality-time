"""Unit tests for the GitLab jobs collectors."""

from .base import CommonGitLabJobsTestsMixin, GitLabJobsTestCase


class GitLabFailedJobsTest(CommonGitLabJobsTestsMixin, GitLabJobsTestCase):
    """Unit tests for the GitLab failed jobs metric."""

    METRIC_TYPE = "failed_jobs"

    def setUp(self):
        """Extend to add the number of consecutive failures to the expected entities."""
        super().setUp()
        for entity in self.expected_entities:
            entity["failure_count"] = "1"

    @staticmethod
    def failed_job2_run(job_id: str, created_at: str, status: str = "failed") -> dict[str, str]:
        """Return a previous run of the second job."""
        return {
            "id": job_id,
            "status": status,
            "name": "job2",
            "stage": "stage",
            "created_at": created_at,
            "web_url": f"https://gitlab/jobs/{job_id}",
            "ref": "develop",
        }

    async def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        measurement = await self.collect_measurement(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(measurement, value="2", entities=self.expected_entities, landing_url=self.LANDING_URL)

    async def test_nr_of_failed_jobs_without_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        for job in self.gitlab_jobs_json:
            job["status"] = "success"
        measurement = await self.collect_measurement(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(measurement, value="0", entities=[], landing_url=self.LANDING_URL)

    async def test_no_jobs_in_lookback_period(self):
        """Test that the number of failed jobs is returned."""
        self.set_source_parameter("lookback_days", "3")
        measurement = await self.collect_measurement(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(measurement, value="0", entities=[], landing_url=self.LANDING_URL)

    async def test_ignore_previous_runs_of_jobs(self):
        """Test that previous runs of the same job are ignored."""
        self.gitlab_jobs_json.extend(
            [
                {
                    "id": "3",
                    "status": "success",
                    "name": "job1",
                    "stage": "stage",
                    "created_at": "2018-03-31T19:41:39.927Z",
                    "web_url": "https://gitlab/jobs/3",
                    "ref": "main",
                },
                {
                    "id": "4",
                    "status": "success",
                    "name": "job1",
                    "stage": "stage",
                    "created_at": "2020-03-31T19:41:39.927Z",
                    "web_url": "https://gitlab/jobs/4",
                    "ref": "main",
                },
            ],
        )
        measurement = await self.collect_measurement(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(
            measurement, value="1", entities=self.expected_entities[-1:], landing_url=self.LANDING_URL
        )

    async def test_minimum_number_of_failures(self):
        """Test that jobs that failed fewer times in a row than the minimum are not counted."""
        self.set_source_parameter("minimum_number_of_failures", "2")
        measurement = await self.collect_measurement(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(measurement, value="0", entities=[], landing_url=self.LANDING_URL)

    async def test_consecutive_failures(self):
        """Test that jobs that failed at least the minimum number of times in a row are counted."""
        self.set_source_parameter("minimum_number_of_failures", "2")
        self.gitlab_jobs_json.append(self.failed_job2_run("5", "2019-03-31T19:39:39.927Z"))
        expected_entities = self.expected_entities[-1:]
        expected_entities[0]["failure_count"] = "2"
        measurement = await self.collect_measurement(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(measurement, value="1", entities=expected_entities, landing_url=self.LANDING_URL)

    async def test_successful_run_ends_the_sequence_of_failures(self):
        """Test that a successful run before the failed runs ends the sequence of failures."""
        self.set_source_parameter("minimum_number_of_failures", "2")
        self.gitlab_jobs_json.extend(
            [
                self.failed_job2_run("5", "2019-03-31T19:39:39.927Z", status="success"),
                self.failed_job2_run("6", "2019-03-31T19:38:39.927Z"),
            ],
        )
        measurement = await self.collect_measurement(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(measurement, value="0", entities=[], landing_url=self.LANDING_URL)

    async def test_failed_runs_outside_the_lookback_period(self):
        """Test that failed runs outside the look-back period do not count as failures."""
        self.set_source_parameter("lookback_days", "20000")  # Look back to about 1971
        self.set_source_parameter("minimum_number_of_failures", "2")
        self.gitlab_jobs_json.append(self.failed_job2_run("5", "1970-03-31T19:39:39.927Z"))
        measurement = await self.collect_measurement(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(measurement, value="0", entities=[], landing_url=self.LANDING_URL)

    async def test_private_token(self):
        """Test that the private token is used."""
        self.set_source_parameter("private_token", "token")
        measurement = await self.collect_measurement(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(
            measurement,
            value="2",
            api_url="https://gitlab/api/v4/projects/namespace%2Fproject/jobs?per_page=100",
            landing_url=self.LANDING_URL,
        )
