"""Unit tests for the random number source."""

import unittest

from metric_collectors import MetricCollector
from source_collectors import Random


class RandomNumberTest(unittest.TestCase):
    """Unit tests for the random number metrics."""

    def test_violations(self):
        """Test the number of violations."""
        metric = dict(type="violations", addition="sum", sources=dict(a=dict(type="random")))
        response = MetricCollector(metric, dict()).get()
        self.assertTrue(Random.min <= int(response["sources"][0]["value"]) <= Random.max)
