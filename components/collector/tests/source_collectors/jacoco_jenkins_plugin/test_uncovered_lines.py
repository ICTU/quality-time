"""Unit tests for the JaCoCo Jenkins plugin uncovered lines collector."""

from typing import ClassVar

from .base import JaCoCoJenkinsPluginTestCase


class JaCoCoJenkinsPluginTest(JaCoCoJenkinsPluginTestCase):
    """Unit tests for the JaCoCo Jenkins plugin uncovered lines collector."""

    METRIC_TYPE = "uncovered_lines"
    JACOCO_JENKINS_PLUGIN_JSON: ClassVar[dict[str, dict[str, int]]] = {"lineCoverage": {"total": 6, "missed": 2}}

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        response = await self.collect(get_request_json_return_value=self.JACOCO_JENKINS_PLUGIN_JSON)
        self.assert_measurement(response, value="2", total="6")
