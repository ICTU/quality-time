"""Unit tests for the Cobertura Jenkins plugin uncovered lines collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTestCase


class CoberturaJenkinsPluginUncoveredLinesTest(JenkinsPluginTestCase):
    """Unit tests for the Cobertura Jenkins plugin uncovered lines collector."""

    SOURCE_TYPE = "cobertura_jenkins_plugin"
    METRIC_TYPE = "uncovered_lines"

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        response = await self.collect(
            self.metric,
            get_request_json_return_value=dict(
                results=dict(elements=[dict(denominator=15, numerator=13, name="Lines")])
            ),
        )
        self.assert_measurement(response, value="2", total="15")
