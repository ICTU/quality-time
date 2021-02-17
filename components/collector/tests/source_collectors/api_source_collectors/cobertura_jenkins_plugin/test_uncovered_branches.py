"""Unit tests for the Cobertura Jenkins plugin uncovered branches collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTestCase


class CoberturaJenkinsPluginUncoveredBranchesTest(JenkinsPluginTestCase):
    """Unit tests for the Cobertura Jenkins plugin uncovered branches collector."""

    SOURCE_TYPE = "cobertura_jenkins_plugin"
    METRIC_TYPE = "uncovered_branches"

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the total number of branches are returned."""
        response = await self.collect(
            self.metric,
            get_request_json_return_value=dict(
                results=dict(elements=[dict(denominator=15, numerator=15, name="Conditionals")])
            ),
        )
        self.assert_measurement(response, value="0", total="15")
