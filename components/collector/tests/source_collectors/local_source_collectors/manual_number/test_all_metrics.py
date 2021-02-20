"""Unit tests for the manual number source."""

from ...source_collector_test_case import SourceCollectorTestCase


class ManualNumberTest(SourceCollectorTestCase):
    """Unit tests for the manual number collectors."""

    SOURCE_TYPE = "manual_number"
    METRIC_TYPE = "violations"

    def setUp(self):
        """Extend to set the number parameter."""
        super().setUp()
        self.sources["source_id"]["parameters"]["number"] = "42"

    async def test_violations(self):
        """Test the number of violations."""
        response = await self.collect(self.metric)
        self.assert_measurement(response, value="42", total="100")

    async def test_percentage(self):
        """Test that the manual source can also be a metric source for metrics with a percentage scale."""
        self.metric["scale"] = "percentage"
        response = await self.collect(self.metric)
        self.assert_measurement(response, value="42", total="100")
