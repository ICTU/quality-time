"""Unit tests for the Jenkins source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JenkinsTestCase(SourceCollectorTestCase):
    """Fixture for Jenkins unit tests."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(type="jenkins", parameters=dict(url="https://jenkins/", failure_type=["Failure"])))
        self.builds = [dict(result="FAILURE", timestamp="1552686540953")]
        self.job_url = "https://job"
        self.job2_url = "https://job2"


class JenkinsFailedJobsTest(JenkinsTestCase):
    """Unit tests for the failed jobs metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="failed_jobs", sources=self.sources, addition="sum")

    async def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        jenkins_json = dict(
            jobs=[
                dict(
                    name="job", url=self.job_url, buildable=True, color="red", builds=self.builds,
                    jobs=[
                        dict(
                            name="child_job", url="https://child_job", buildable=True, color="red",
                            builds=self.builds)])])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="2")

    async def test_failed_jobs(self):
        """Test that the failed jobs are returned."""
        jenkins_json = dict(
            jobs=[dict(name="job", url=self.job_url, buildable=True, color="red", builds=self.builds)])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job", name="job", url=self.job_url)]
        self.assert_measurement(response, entities=expected_entities)

    async def test_ignore_jobs(self):
        """Test that a failed job can be ignored."""
        self.sources["source_id"]["parameters"]["jobs_to_ignore"] = ["job2"]
        jenkins_json = dict(
            jobs=[dict(name="job", url=self.job_url, buildable=True, color="red", builds=self.builds),
                  dict(name="job2", url=self.job2_url, buildable=True, color="red", builds=self.builds)])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job", name="job", url=self.job_url)]
        self.assert_measurement(response, entities=expected_entities)

    async def test_ignore_jobs_by_regular_expression(self):
        """Test that failed jobs can be ignored by regular expression."""
        self.sources["source_id"]["parameters"]["jobs_to_ignore"] = ["job."]
        jenkins_json = dict(
            jobs=[dict(name="job", url=self.job_url, buildable=True, color="red", builds=self.builds),
                  dict(name="job2", url=self.job2_url, buildable=True, color="red", builds=self.builds)])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job", name="job", url=self.job_url)]
        self.assert_measurement(response, entities=expected_entities)

    async def test_no_builds(self):
        """Test no builds."""
        jenkins_json = dict(jobs=[dict(name="job", url=self.job_url, buildable=True, color="notbuilt", builds=[])])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, entities=[])


class JenkinsUnusedJobsTest(JenkinsTestCase):
    """Unit tests for the unused jobs metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="unused_jobs", sources=self.sources, addition="sum")

    async def test_unused_jobs(self):
        """Test that the number of unused jobs is returned."""
        jenkins_json = dict(
            jobs=[dict(
                name="job", url=self.job_url, buildable=True, color="red", builds=[dict(timestamp="1548311610349")])])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="1")

    async def test_unbuild_job(self):
        """Test that jobs without builds are ignored."""
        jenkins_json = dict(jobs=[dict(name="job", url=self.job_url, buildable=True, color="red")])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="0")
