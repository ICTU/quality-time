"""Unit tests for the JaCoCo Jenkins plugin source."""

from .jenkins_plugin_test_case import JenkinsPluginTestCase, JenkinsPluginTestsMixin


class JaCoCoJenkinsPluginTest(JenkinsPluginTestCase, JenkinsPluginTestsMixin):
    """Unit tests for the JaCoCo Jenkins plugin metrics."""

    source_type = "jacoco_jenkins_plugin"

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=dict(lineCoverage=dict(total=6, missed=2)))
        self.assert_measurement(response, value="2", total="6")

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches and the total number of branches are returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = await self.collect(
            metric, get_request_json_return_value=dict(branchCoverage=dict(total=6, missed=2)))
        self.assert_measurement(response, value="2", total="6")
