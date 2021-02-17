"""Unit tests for the JaCoCo Jenkins plugin uncovered branches collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTestCase


class JaCoCoJenkinsPluginTest(JenkinsPluginTestCase):
    """Unit tests for the JaCoCo Jenkins plugin uncovered branches collector."""

    SOURCE_TYPE = "jacoco_jenkins_plugin"
    METRIC_TYPE = "uncovered_branches"

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the total number of branches are returned."""
        response = await self.collect(
            self.metric, get_request_json_return_value=dict(branchCoverage=dict(total=6, missed=2))
        )
        self.assert_measurement(response, value="2", total="6")
