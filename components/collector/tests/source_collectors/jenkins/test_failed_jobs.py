"""Unit tests for the Jenkins failed jobs collector."""

from datetime import datetime, timedelta

from dateutil.tz import tzutc

from collector_utilities.date_time import datetime_from_timestamp

from .base import JenkinsTestCase


class JenkinsFailedJobsTest(JenkinsTestCase):
    """Unit tests for the Jenkins failed jobs collector."""

    METRIC_TYPE = "failed_jobs"

    def jenkins_json(self, nr_jobs: int = 1, builds: list | None = None, buildable: bool = True) -> dict:
        """Create a Jenkins JSON fixture."""
        builds = self.builds if builds is None else builds
        jobs = [
            {
                "name": f"job{index}",
                "url": f"https://job{index}",
                "buildable": buildable,
                "color": "red",
                "builds": builds,
            }
            for index in range(1, nr_jobs + 1)
        ]
        return {"jobs": jobs}

    def timestamp(self, days_ago: int = 0) -> int:
        """Return a Jenkins timestamp."""
        return round((datetime.now(tz=tzutc()) - timedelta(days=days_ago)).timestamp() * 1000)

    def expected_entity(
        self,
        build_date: str = "",
        build_datetime: datetime | None = None,
        build_result: str = "Failure",
        job_nr: int = 1,
    ):
        """Return an expected entity."""
        build_date = build_date or "2019-03-15"
        build_datetime = build_datetime or datetime_from_timestamp(self.builds[0]["timestamp"])
        return {
            "build_date": build_date,
            "build_datetime": build_datetime,
            "build_result": build_result,
            "key": f"job{job_nr}",
            "name": f"job{job_nr}",
            "url": f"https://job{job_nr}",
        }

    async def test_failed_child_job(self):
        """Test that the number of failed jobs is returned, including failed child jobs."""
        jenkins_json = self.jenkins_json(nr_jobs=2)
        jenkins_json["jobs"][0]["jobs"] = [
            {"name": "child_job", "url": "https://child_job", "buildable": True, "color": "red", "builds": self.builds},
        ]
        response = await self.collect(get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="3")

    async def test_failed_jobs(self):
        """Test that the failed jobs are returned."""
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=1))
        self.assert_measurement(response, entities=[self.expected_entity()])

    async def test_ignore_unbuildable_failed_jobs(self):
        """Test that the unbuildable failed jobs are ignored."""
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=1, buildable=False))
        self.assert_measurement(response, entities=[])

    async def test_include_jobs(self):
        """Test that any job that is not explicitly included fails if jobs_to_include is not empty."""
        self.set_source_parameter("jobs_to_include", ["job1"])
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=2))
        self.assert_measurement(response, entities=[self.expected_entity()])

    async def test_include_jobs_by_regular_expression(self):
        """Test that any job that is not explicitly included fails if jobs_to_include is not empty."""
        self.set_source_parameter("jobs_to_include", ["job[23]"])
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=2))
        self.assert_measurement(response, entities=[self.expected_entity(job_nr=2)])

    async def test_ignore_jobs(self):
        """Test that a failed job can be ignored."""
        self.set_source_parameter("jobs_to_ignore", ["job2"])
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=2))
        self.assert_measurement(response, entities=[self.expected_entity()])

    async def test_ignore_jobs_by_regular_expression(self):
        """Test that failed jobs can be ignored by regular expression."""
        self.set_source_parameter("jobs_to_ignore", ["job[23]"])
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=2))
        self.assert_measurement(response, entities=[self.expected_entity()])

    async def test_include_and_ignore_jobs(self):
        """Test that jobs can be included and ignored."""
        self.set_source_parameter("jobs_to_include", ["job."])
        self.set_source_parameter("jobs_to_ignore", [".*2"])
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=2))
        self.assert_measurement(response, entities=[self.expected_entity()])

    async def test_no_builds(self):
        """Test no builds."""
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=1, builds=[]))
        self.assert_measurement(response, entities=[])

    async def test_ignore_job_if_all_failed_builds_are_in_the_grace_period(self):
        """Test that jobs can be ignored by grace period."""
        self.set_source_parameter("grace_days", "5")
        builds = [
            {"result": "FAILURE", "timestamp": self.timestamp()},
            {"result": "FAILURE", "timestamp": self.timestamp(days_ago=4)},
        ]
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=1, builds=builds))
        self.assert_measurement(response, entities=[])

    async def test_do_not_ignore_job_if_not_all_failed_builds_are_in_the_grace_period(self):
        """Test that jobs can be ignored by grace period."""
        self.set_source_parameter("grace_days", "5")
        old_build_timestamp = self.timestamp(days_ago=6)
        builds = [
            {"result": "FAILURE", "timestamp": self.timestamp()},
            {"result": "FAILURE", "timestamp": old_build_timestamp},
        ]
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=1, builds=builds))
        expected_entity = self.expected_entity(
            build_date=datetime_from_timestamp(old_build_timestamp).date().isoformat(),
            build_datetime=datetime_from_timestamp(old_build_timestamp),
        )
        self.assert_measurement(response, entities=[expected_entity])

    async def test_grace_period_does_not_impact_successful_job_with_failure_in_grace_period(self):
        """Test that jobs can be ignored by grace period."""
        self.set_source_parameter("grace_days", "5")
        builds = [
            {"result": "SUCCESS", "timestamp": self.timestamp()},
            {"result": "FAILURE", "timestamp": self.timestamp(days_ago=4)},
        ]
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=1, builds=builds))
        self.assert_measurement(response, entities=[])

    async def test_grace_period_does_not_impact_successful_job_with_failure_before_grace_period(self):
        """Test that jobs can be ignored by grace period."""
        self.set_source_parameter("grace_days", "5")
        builds = [
            {"result": "SUCCESS", "timestamp": self.timestamp()},
            {"result": "FAILURE", "timestamp": self.timestamp(days_ago=6)},
        ]
        response = await self.collect(get_request_json_return_value=self.jenkins_json(nr_jobs=1, builds=builds))
        self.assert_measurement(response, entities=[])
