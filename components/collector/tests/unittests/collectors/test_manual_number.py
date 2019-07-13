"""Unit tests for the manual number source."""

import unittest

from src.collector import MetricCollector


class ManualNumberTest(unittest.TestCase):
    """Unit tests for the manual number metrics."""

    def test_violations(self):
        """Test the number of violations."""
        metric = dict(
            type="violations", addition="sum", sources=dict(a=dict(type="manual_number", parameters=dict(number="42"))))
        response = MetricCollector(metric).get()
        self.assertEqual("42", response["sources"][0]["value"])
