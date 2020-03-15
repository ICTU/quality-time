"""Unit tests for the manual number source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class ManualNumberTest(SourceCollectorTestCase):
    """Unit tests for the manual number metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="manual_number", parameters=dict(number="42")))

    async def test_violations(self):
        """Test the number of violations."""
        metric = dict(type="violations", addition="sum", scale="count", sources=self.sources)
        response = await self.collect(metric)
        self.assert_measurement(response, value="42", total="100")

    async def test_percentage(self):
        """Test that the manual source can also be a metric source for metrics with a percentage scale."""
        metric = dict(type="violations", addition="sum", scale="percentage", sources=self.sources)
        response = await self.collect(metric)
        self.assert_measurement(response, value="42", total="100")
