"""Unit tests for the JaCoCo Jenkins plugin uncovered lines collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTestCase


class JaCoCoJenkinsPluginTest(JenkinsPluginTestCase):
    """Unit tests for the JaCoCo Jenkins plugin uncovered lines collector."""

    SOURCE_TYPE = "jacoco_jenkins_plugin"
    METRIC_TYPE = "uncovered_lines"

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        json = dict(lineCoverage=dict(total=6, missed=2))
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="2", total="6")
