"""Unit tests for the Cobertura Jenkins plugin uncovered branches collector."""

from .base import CoberturaJenkinsPluginCoverageTestCase


class CoberturaJenkinsPluginUncoveredBranchesTest(CoberturaJenkinsPluginCoverageTestCase):
    """Unit tests for the Cobertura Jenkins plugin uncovered branches collector."""

    SOURCE_TYPE = "cobertura_jenkins_plugin"
    METRIC_TYPE = "uncovered_branches"

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the total number of branches are returned."""
        response = await self.collect(self.metric, get_request_json_return_value=self.cobertura_jenkins_plugin_json)
        self.assert_measurement(response, value="0", total="15")
