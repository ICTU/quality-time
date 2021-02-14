"""Unit tests for the Cobertura Jenkins plugin uncovered branches collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTestCase, JenkinsPluginTestsMixin


class CoberturaJenkinsPluginUncoveredBranchesTest(JenkinsPluginTestCase, JenkinsPluginTestsMixin):
    """Unit tests for the Cobertura Jenkins plugin uncovered branches collector."""

    source_type = "cobertura_jenkins_plugin"

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the total number of branches are returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                results=dict(elements=[dict(denominator=15, numerator=15, name="Conditionals")])
            ),
        )
        self.assert_measurement(response, value="0", total="15")
