"""Unit tests for the Cobertura Jenkins plugin source."""

from .jenkins_plugin_test_case import JenkinsPluginTestCase, JenkinsPluginTestsMixin


class CoberturaJenkinsPluginTest(JenkinsPluginTestCase, JenkinsPluginTestsMixin):
    """Unit tests for the Cobertura Jenkins plugin metrics."""

    source_type = "cobertura_jenkins_plugin"

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                results=dict(elements=[dict(denominator=15, numerator=13, name="Lines")])))
        self.assert_measurement(response, value="2", total="15")

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the total number of branches are returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                results=dict(elements=[dict(denominator=15, numerator=15, name="Conditionals")])))
        self.assert_measurement(response, value="0", total="15")
