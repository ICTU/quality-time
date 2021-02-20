"""Unit tests for the JaCoCo Jenkins plugin uncovered branches collector."""

from .base import JaCoCoJenkinsPluginTestCase


class JaCoCoJenkinsPluginUncoveredBranchesTest(JaCoCoJenkinsPluginTestCase):
    """Unit tests for the JaCoCo Jenkins plugin uncovered branches collector."""

    METRIC_TYPE = "uncovered_branches"
    JACOCO_JENKINS_PLUGIN_JSON = dict(branchCoverage=dict(total=6, missed=2))

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the total number of branches are returned."""
        response = await self.collect(get_request_json_return_value=self.JACOCO_JENKINS_PLUGIN_JSON)
        self.assert_measurement(response, value="2", total="6")
