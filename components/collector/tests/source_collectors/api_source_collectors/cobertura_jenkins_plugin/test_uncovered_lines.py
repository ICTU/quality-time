"""Unit tests for the Cobertura Jenkins plugin uncovered lines collector."""

from .base import CoberturaJenkinsPluginTestCase


class CoberturaJenkinsPluginUncoveredLinesTest(CoberturaJenkinsPluginTestCase):
    """Unit tests for the Cobertura Jenkins plugin uncovered lines collector."""

    METRIC_TYPE = "uncovered_lines"
    COBERTURA_JENKINS_PLUGIN_JSON = dict(results=dict(elements=[dict(denominator=15, numerator=13, name="Lines")]))

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        response = await self.collect(self.metric, get_request_json_return_value=self.COBERTURA_JENKINS_PLUGIN_JSON)
        self.assert_measurement(response, value="2", total="15")
