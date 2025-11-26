"""Unit tests for the Jenkins source up-to-dateness collector."""

from collector_utilities.date_time import datetime_from_timestamp, days_ago

from .base import JenkinsTestCase


class JenkinsSourceUpToDatenessTest(JenkinsTestCase):
    """Unit tests for the Jenkins source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_job(self):
        """Test that the age of the last build is returned."""
        jenkins_json = {
            "jobs": [{"name": "job", "url": self.job_url, "buildable": True, "color": "red", "builds": self.builds}],
        }
        response = await self.collect(get_request_json_return_value=jenkins_json)
        expected_dt = datetime_from_timestamp(self.builds[0]["timestamp"])
        expected_entities = [
            {
                "build_date": "2019-03-15",
                "build_datetime": expected_dt,
                "build_result": "Failure",
                "key": "job",
                "name": "job",
                "url": self.job_url,
            },
        ]
        self.assert_measurement(response, value=str(days_ago(expected_dt)), entities=expected_entities)

    async def test_job_without_builds(self):
        """Test that the age is None when the job has no builds."""
        jenkins_json = {"jobs": [{"name": "job", "url": self.job_url, "buildable": True, "color": "red", "builds": []}]}
        response = await self.collect(get_request_json_return_value=jenkins_json)
        expected_entities = [
            {
                "build_date": "",
                "build_datetime": None,
                "build_result": "Not built",
                "key": "job",
                "name": "job",
                "url": self.job_url,
            },
        ]
        self.assert_measurement(response, value=None, entities=expected_entities)

    async def test_ignore_failed_builds(self):
        """Test that failed builds can be ignored."""
        success_dt = 1552686531953
        self.set_source_parameter("result_type", ["Success"])
        jenkins_json = {
            "jobs": [{"name": "job", "url": self.job_url, "buildable": True, "color": "red", "builds": self.builds}],
        }
        response = await self.collect(get_request_json_return_value=jenkins_json)
        expected_dt = datetime_from_timestamp(success_dt)
        expected_entities = [
            {
                "build_date": "2019-03-15",
                "build_datetime": expected_dt,
                "build_result": "Success",
                "key": "job",
                "name": "job",
                "url": self.job_url,
            },
        ]
        self.assert_measurement(response, value=str(days_ago(expected_dt)), entities=expected_entities)
