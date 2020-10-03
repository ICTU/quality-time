"""Unit tests for the Robot Framework Jenkins plugin source."""

from .jenkins_plugin_test_case import JenkinsPluginTestCase, JenkinsPluginTestsMixin


class RobotFrameworkJenkinsPluginTest(JenkinsPluginTestCase, JenkinsPluginTestsMixin):
    """Unit tests for the Robot Framework Jenkins plugin metrics."""

    source_type = "robot_framework_jenkins_plugin"

    def setUp(self):
        super().setUp()
        self.jenkins_json = dict(overallTotal=2, overallFailed=1, overallPassed=1)

    async def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=self.jenkins_json)
        self.assert_measurement(response, value="2", total="2")

    async def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=self.jenkins_json)
        self.assert_measurement(response, value="1", total="2")
