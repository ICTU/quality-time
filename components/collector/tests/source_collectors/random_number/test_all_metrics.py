"""Unit tests for the random number collector."""

from source_collectors import Random

from ..source_collector_test_case import SourceCollectorTestCase


class RandomNumberTest(SourceCollectorTestCase):
    """Unit tests for the random number collector."""

    SOURCE_TYPE = "random"
    METRIC_TYPE = "violations"

    async def test_violations(self):
        """Test the number of violations."""
        response = await self.collect(self.metric)
        self.assertTrue(Random.MIN <= int(response["sources"][0]["value"]) <= Random.MAX)
