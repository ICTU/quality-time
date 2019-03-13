"""Unit tests for the random number source."""

import unittest

from collector.collector import Collector, collect_measurement
from collector.collectors import Random


class RandomNumberTest(unittest.TestCase):
    """Unit tests for the random number metrics."""

    def setUp(self):
        """Test fixture."""
        Collector.RESPONSE_CACHE.clear()

    def test_violations(self):
        """Test the number of violations."""
        metric = dict(type="violations", sources=dict(a=dict(type="random")))
        response = collect_measurement(metric)
        self.assertTrue(Random.min <= int(response["sources"][0]["value"]) <= Random.max)
