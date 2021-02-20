"""Unit tests for the Jenkins failed jobs collector."""

from .base import JenkinsTestCase


class JenkinsFailedJobsTest(JenkinsTestCase):
    """Unit tests for the Jenkins failed jobs collector."""

    METRIC_TYPE = "failed_jobs"

    def setUp(self):
        """Extend to set up Jenkins data."""
        super().setUp()
        self.jenkins_json = dict(
            jobs=[
                dict(name="job", url=self.job_url, buildable=True, color="red", builds=self.builds),
                dict(name="job2", url=self.job2_url, buildable=True, color="red", builds=self.builds),
            ]
        )

    async def test_failed_child_job(self):
        """Test that the number of failed jobs is returned, including failed child jobs."""
        self.jenkins_json["jobs"][0]["jobs"] = [
            dict(name="child_job", url="https://child_job", buildable=True, color="red", builds=self.builds)
        ]
        response = await self.collect(self.metric, get_request_json_return_value=self.jenkins_json)
        self.assert_measurement(response, value="3")

    async def test_failed_jobs(self):
        """Test that the failed jobs are returned."""
        jenkins_json = dict(jobs=[dict(name="job", url=self.job_url, buildable=True, color="red", builds=self.builds)])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job", name="job", url=self.job_url)
        ]
        self.assert_measurement(response, entities=expected_entities)

    async def test_include_jobs(self):
        """Test that any job that is not explicitly included fails if jobs_to_include is not empty."""
        self.sources["source_id"]["parameters"]["jobs_to_include"] = ["job"]
        response = await self.collect(self.metric, get_request_json_return_value=self.jenkins_json)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job", name="job", url=self.job_url)
        ]
        self.assert_measurement(response, entities=expected_entities)

    async def test_include_jobs_by_regular_expression(self):
        """Test that any job that is not explicitly included fails if jobs_to_include is not empty."""
        self.sources["source_id"]["parameters"]["jobs_to_include"] = ["job."]
        response = await self.collect(self.metric, get_request_json_return_value=self.jenkins_json)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job2", name="job2", url=self.job2_url)
        ]
        self.assert_measurement(response, entities=expected_entities)

    async def test_ignore_jobs(self):
        """Test that a failed job can be ignored."""
        self.sources["source_id"]["parameters"]["jobs_to_ignore"] = ["job2"]
        response = await self.collect(self.metric, get_request_json_return_value=self.jenkins_json)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job", name="job", url=self.job_url)
        ]
        self.assert_measurement(response, entities=expected_entities)

    async def test_ignore_jobs_by_regular_expression(self):
        """Test that failed jobs can be ignored by regular expression."""
        self.sources["source_id"]["parameters"]["jobs_to_ignore"] = ["job."]
        response = await self.collect(self.metric, get_request_json_return_value=self.jenkins_json)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job", name="job", url=self.job_url)
        ]
        self.assert_measurement(response, entities=expected_entities)

    async def test_include_and_ignore_jobs(self):
        """Test that jobs can be included and ignored."""
        self.sources["source_id"]["parameters"]["jobs_to_include"] = ["job."]
        self.sources["source_id"]["parameters"]["jobs_to_ignore"] = [".*2"]
        self.jenkins_json["jobs"].append(
            dict(name="job3", url="https://job3", buildable=True, color="red", builds=self.builds)
        )
        response = await self.collect(self.metric, get_request_json_return_value=self.jenkins_json)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job3", name="job3", url="https://job3")
        ]
        self.assert_measurement(response, entities=expected_entities)

    async def test_no_builds(self):
        """Test no builds."""
        jenkins_json = dict(jobs=[dict(name="job", url=self.job_url, buildable=True, color="notbuilt", builds=[])])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, entities=[])
