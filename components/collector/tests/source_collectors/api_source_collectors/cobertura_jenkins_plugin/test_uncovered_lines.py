"""Unit tests for the Cobertura Jenkins plugin uncovered lines collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTestCase, JenkinsPluginTestsMixin


class CoberturaJenkinsPluginUncoveredLinesTest(JenkinsPluginTestCase, JenkinsPluginTestsMixin):
    """Unit tests for the Cobertura Jenkins plugin uncovered lines collector."""

    source_type = "cobertura_jenkins_plugin"

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                results=dict(elements=[dict(denominator=15, numerator=13, name="Lines")])
            ),
        )
        self.assert_measurement(response, value="2", total="15")
