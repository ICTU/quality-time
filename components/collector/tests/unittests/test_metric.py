"""Unit tests for the metric class."""

import unittest

from collector.metric import Metric
from collector.type import Measurement


class MetricTest(unittest.TestCase):
    """Unit tests for the metric class."""

    def test_sum(self):
        """Test that two measurements can be added."""
        self.assertEqual(Measurement("7"), Metric(dict()).sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum(self):
        """Test that two measurements can be added safely."""
        self.assertEqual((Measurement("7"), None),
                         Metric(dict()).safely_sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum_with_error(self):
        """Test that an error message is returned when adding fails."""
        measurement, error_message = Metric(dict()).safely_sum([Measurement("4"), Measurement("abc")])
        self.assertEqual(None, measurement)
        self.assertTrue(error_message.startswith("Traceback"))

    def test_safely_sum_with_none(self):
        """Test that None is returned if one of the input measurements is None."""
        measurement, error_message = Metric(dict()).safely_sum([Measurement("4"), None])
        self.assertEqual(None, measurement)
        self.assertEqual(None, error_message)

    def test_default_target(self):
        """Test that the default target is included in the response."""
        source_response = dict(source=dict(responses=[dict(measurement=Measurement("1"))]))
        measurement_response = Metric(dict()).get(source_response)
        self.assertEqual(Measurement("0"), measurement_response["metric"]["default_target"])
