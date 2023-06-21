"""Unit tests for the Cobertura Jenkins plugin uncovered branches collector."""

from typing import ClassVar

from .base import CoberturaJenkinsPluginTestCase


class CoberturaJenkinsPluginUncoveredBranchesTest(CoberturaJenkinsPluginTestCase):
    """Unit tests for the Cobertura Jenkins plugin uncovered branches collector."""

    METRIC_TYPE = "uncovered_branches"
    COBERTURA_JENKINS_PLUGIN_JSON: ClassVar[dict[str, dict[str, list[dict[str, int | str]]]]] = {
        "results": {"elements": [{"denominator": 15, "numerator": 15, "name": "Conditionals"}]},
    }

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the total number of branches are returned."""
        response = await self.collect(get_request_json_return_value=self.COBERTURA_JENKINS_PLUGIN_JSON)
        self.assert_measurement(response, value="0", total="15")
