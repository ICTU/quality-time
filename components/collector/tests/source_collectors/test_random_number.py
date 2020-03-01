"""Unit tests for the random number source."""

from source_collectors import Random
from .source_collector_test_case import SourceCollectorTestCase


class RandomNumberTest(SourceCollectorTestCase):
    """Unit tests for the random number metrics."""

    async def test_violations(self):
        """Test the number of violations."""
        metric = dict(type="violations", addition="sum", sources=dict(a=dict(type="random")))
        response = await self.collect(metric)
        self.assertTrue(Random.MIN <= int(response["sources"][0]["value"]) <= Random.MAX)
