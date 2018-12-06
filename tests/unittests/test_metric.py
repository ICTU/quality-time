import unittest

from quality_time.metric import Metric
from quality_time.type import Measurement


class MetricTest(unittest.TestCase):
    """Unit tests for the metric class."""
    def test_name(self):
        self.assertEqual("Metric", Metric.name())

    def test_sum(self):
        """Test that two measurements can be added."""
        self.assertEqual(Measurement("7"), Metric.sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum(self):
        """Test that two measurements can be added safely."""
        self.assertEqual((Measurement("7"), None), Metric.safely_sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum_with_error(self):
        """Test that an error message is returned when adding fails."""
        measurement, error_message = Metric.safely_sum([Measurement("4"), Measurement("abc")])
        self.assertEqual(None, measurement)
        self.assertTrue(error_message.startswith("Traceback"))
