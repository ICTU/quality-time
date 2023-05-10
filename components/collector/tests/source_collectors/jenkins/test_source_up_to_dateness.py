"""Unit tests for the Jenkins source up-to-dateness collector."""

from collector_utilities.date_time import days_ago, datetime_fromparts

from .base import JenkinsTestCase


class JenkinsSourceUpToDatenessTest(JenkinsTestCase):
    """Unit tests for the Jenkins source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_job(self):
        """Test that the age of the last build is returned."""
        jenkins_json = {
            "jobs": [{"name": "job", "url": self.job_url, "buildable": True, "color": "red", "builds": self.builds}],
        }
        response = await self.collect(get_request_json_return_value=jenkins_json)
        expected_value = str(days_ago(datetime_fromparts(2019, 3, 15)))
        expected_entities = [
            {"build_date": "2019-03-15", "build_status": "Failure", "key": "job", "name": "job", "url": self.job_url},
        ]
        self.assert_measurement(response, value=expected_value, entities=expected_entities)

    async def test_job_without_builds(self):
        """Test that the age is None when the job has no builds."""
        jenkins_json = {"jobs": [{"name": "job", "url": self.job_url, "buildable": True, "color": "red", "builds": []}]}
        response = await self.collect(get_request_json_return_value=jenkins_json)
        expected_entities = [
            {"build_date": "", "build_status": "Not built", "key": "job", "name": "job", "url": self.job_url},
        ]
        self.assert_measurement(response, value=None, entities=expected_entities)

    async def test_ignore_failed_builds(self):
        """Test that failed builds can be ignored."""
        self.set_source_parameter("result_type", ["Success"])
        self.builds.append({"result": "SUCCESS", "timestamp": 1553686540953})
        jenkins_json = {
            "jobs": [{"name": "job", "url": self.job_url, "buildable": True, "color": "red", "builds": self.builds}],
        }
        response = await self.collect(get_request_json_return_value=jenkins_json)
        expected_value = str(days_ago(datetime_fromparts(2019, 3, 27)))
        expected_entities = [
            {"build_date": "2019-03-27", "build_status": "Success", "key": "job", "name": "job", "url": self.job_url},
        ]
        self.assert_measurement(response, value=expected_value, entities=expected_entities)
