"""Unit tests for the JaCoCo Jenkins plugin uncovered branches collector."""

from .base import JaCoCoJenkinsPluginCoverageTestCase


class JaCoCoJenkinsPluginTest(JaCoCoJenkinsPluginCoverageTestCase):
    """Unit tests for the JaCoCo Jenkins plugin uncovered branches collector."""

    SOURCE_TYPE = "jacoco_jenkins_plugin"
    METRIC_TYPE = "uncovered_branches"

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the total number of branches are returned."""
        response = await self.collect(self.metric, get_request_json_return_value=self.jacoco_jenkins_plugin_json)
        self.assert_measurement(response, value="2", total="6")
