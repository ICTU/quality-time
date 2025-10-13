"""Unit tests for the Jenkins pipeline duration collector."""

from .base import JenkinsTestCase


class JenkinsPipelineDurationTest(JenkinsTestCase):
    """Unit tests for the Jenkins pipeline duration collector."""

    METRIC_TYPE = "pipeline_duration"
    METRIC_ADDITION = "max"

    def setUp(self):
        """Extend to set up Jenkins data."""
        super().setUp()
        self.set_source_parameter("pipeline", "pipeline")
        self.jenkins_json = {
            "jobs": [
                {"name": "main", "builds": [{"result": "FAILURE", "duration": 600_000, "url": "https://failure"}]},
                {"name": "dev", "builds": [{"result": "SUCCESS", "duration": 300_000, "url": "https://success"}]},
                {"name": "new branch", "builds": []},
            ],
        }

    async def test_duration(self):
        """Test that the duration is returned."""
        response = await self.collect(get_request_json_return_value=self.jenkins_json)
        self.assert_measurement(response, value="10", landing_url="https://failure")

    async def test_duration_exlude_building(self):
        """Test that building builds are excluded."""
        building_build = {"name": "main", "builds": [{"building": True}]}
        self.jenkins_json["jobs"].insert(0, building_build)
        response = await self.collect(get_request_json_return_value=self.jenkins_json)
        self.assert_measurement(response, value="10", landing_url="https://failure")

    async def test_duration_for_result_type(self):
        """Test that the duration of the build with the specified result type is returned."""
        self.set_source_parameter("result_type", ["Success"])
        response = await self.collect(get_request_json_return_value=self.jenkins_json)
        self.assert_measurement(response, value="5", landing_url="https://success")

    async def test_duration_without_builds(self):
        """Test that the duration is zero if there are no builds."""
        self.set_source_parameter("branches", ["new branch"])
        response = await self.collect(get_request_json_return_value=self.jenkins_json)
        self.assert_measurement(response, value="0", landing_url="https://jenkins/job/pipeline")

    async def test_duration_for_specific_branch(self):
        """Test that the duration of the pipeline for the branch is returned."""
        self.set_source_parameter("branches", ["dev"])
        response = await self.collect(get_request_json_return_value=self.jenkins_json)
        self.assert_measurement(response, value="5", landing_url="https://success")

    async def test_duration_of_workflow_job(self):
        """Test that the duration of a workflow job is returned."""
        jenkins_json = {"builds": [{"result": "FAILURE", "duration": 1_200_000, "url": "https://build"}]}
        response = await self.collect(get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="20", landing_url="https://build")
