"""Unit tests for the random number source."""

from source_collectors import Random
from .source_collector_test_case import SourceCollectorTestCase


class RandomNumberTest(SourceCollectorTestCase):
    """Unit tests for the random number metrics."""

    def test_violations(self):
        """Test the number of violations."""
        metric = dict(type="violations", addition="sum", sources=dict(a=dict(type="random")))
        response = self.collect(metric)
        self.assertTrue(Random.min <= int(response["sources"][0]["value"]) <= Random.max)
        self.assert_no_connection_error(response)
