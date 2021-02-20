"""Unit tests for the Jenkins unused jobs collector."""

from .base import JenkinsTestCase


class JenkinsUnusedJobsTest(JenkinsTestCase):
    """Unit tests for the Jenkins unused jobs collector."""

    METRIC_TYPE = "unused_jobs"

    async def test_unused_jobs(self):
        """Test that the number of unused jobs is returned."""
        jenkins_json = dict(
            jobs=[
                dict(
                    name="job", url=self.job_url, buildable=True, color="red", builds=[dict(timestamp="1548311610349")]
                )
            ]
        )
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="1")

    async def test_unbuild_job(self):
        """Test that jobs without builds are ignored."""
        jenkins_json = dict(jobs=[dict(name="job", url=self.job_url, buildable=True, color="red")])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="0")
