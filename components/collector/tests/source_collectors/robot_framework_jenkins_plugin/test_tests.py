"""Unit tests for the Robot Framework Jenkins plugin tests collector."""

from .base import RobotFrameworkJenkinsPluginTestCase


class RobotFrameworkJenkinsPluginTest(RobotFrameworkJenkinsPluginTestCase):
    """Unit tests for the Robot Framework Jenkins plugin tests collector."""

    METRIC_TYPE = "tests"
    JENKINS_JSON = {"overallTotal": 2, "overallFailed": 1, "overallPassed": 1}

    async def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        response = await self.collect(get_request_json_return_value=self.JENKINS_JSON)
        self.assert_measurement(response, value="2", total="2")

    async def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        self.set_source_parameter("test_result", ["fail"])
        response = await self.collect(get_request_json_return_value=self.JENKINS_JSON)
        self.assert_measurement(response, value="1", total="2")

    async def test_passed_tests(self):
        """Test that the number of passed tests is returned."""
        self.set_source_parameter("test_result", ["pass"])
        response = await self.collect(get_request_json_return_value=self.JENKINS_JSON)
        self.assert_measurement(response, value="1", total="2")
