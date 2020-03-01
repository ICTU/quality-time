"""Unit tests for the JaCoCo Jenkins plugin source."""

from datetime import datetime

from collector_utilities.functions import days_ago
from .source_collector_test_case import SourceCollectorTestCase


class JaCoCoJenkinsPluginTest(SourceCollectorTestCase):
    """Unit tests for the JaCoCo Jenkins plugin metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="jacoco_jenkins_plugin", parameters=dict(url="https://jenkins/job")))

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

    async def test_source_up_to_dateness(self):
        """Test that the source up to dateness is returned."""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=dict(timestamp="1565284457173"))
        expected_age = days_ago(datetime.fromtimestamp(1565284457173 / 1000.))
        self.assert_measurement(response, value=str(expected_age))
