"""Unit tests for the manual number source."""

import unittest

from metric_collectors import MetricCollector


class ManualNumberTest(unittest.TestCase):
    """Unit tests for the manual number metrics."""

    def test_violations(self):
        """Test the number of violations."""
        datamodel = dict(sources=dict(manual_number=dict(parameters=dict(number=dict()))))
        metric = dict(
            type="violations", addition="sum", sources=dict(a=dict(type="manual_number", parameters=dict(number="42"))))
        response = MetricCollector(metric, datamodel).get()
        self.assertEqual("42", response["sources"][0]["value"])
