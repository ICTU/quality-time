"""Unit tests for the Jenkins source up-to-dateness collector."""

from datetime import date

from .base import JenkinsTestCase


class JenkinsSourceUpToDatenessTest(JenkinsTestCase):
    """Unit tests for the Jenkins source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    ADDITION = "max"

    async def test_job(self):
        """Test that the age of the last build is returned."""
        jenkins_json = dict(jobs=[dict(name="job", url=self.job_url, buildable=True, color="red", builds=self.builds)])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        expected_value = str((date.today() - date.fromisoformat("2019-03-15")).days)
        expected_entities = [
            dict(build_date="2019-03-15", build_status="Failure", key="job", name="job", url=self.job_url)
        ]
        self.assert_measurement(response, value=expected_value, entities=expected_entities)

    async def test_job_without_builds(self):
        """Test that the age is None when the job has no builds."""
        jenkins_json = dict(jobs=[dict(name="job", url=self.job_url, buildable=True, color="red", builds=[])])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        expected_entities = [dict(build_date="", build_status="Not built", key="job", name="job", url=self.job_url)]
        self.assert_measurement(response, value=None, entities=expected_entities)

    async def test_ignore_failed_builds(self):
        """Test that failed builds can be ignored."""
        self.sources["source_id"]["parameters"]["result_type"] = ["Success"]
        self.builds.append(dict(result="SUCCESS", timestamp="1553686540953"))
        jenkins_json = dict(jobs=[dict(name="job", url=self.job_url, buildable=True, color="red", builds=self.builds)])
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        expected_value = str((date.today() - date.fromisoformat("2019-03-27")).days)
        expected_entities = [
            dict(build_date="2019-03-27", build_status="Success", key="job", name="job", url=self.job_url)
        ]
        self.assert_measurement(response, value=expected_value, entities=expected_entities)
