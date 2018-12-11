"""Unit tests for the metric class."""

import unittest

import bottle

from quality_time.metric import Metric
from quality_time.type import Measurement


class MetricTest(unittest.TestCase):
    """Unit tests for the metric class."""

    def test_sum(self):
        """Test that two measurements can be added."""
        self.assertEqual(Measurement("7"), Metric(bottle.Request()).sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum(self):
        """Test that two measurements can be added safely."""
        self.assertEqual((Measurement("7"), None),
                         Metric(bottle.Request()).safely_sum([Measurement("4"), Measurement("3")]))

    def test_safely_sum_with_error(self):
        """Test that an error message is returned when adding fails."""
        measurement, error_message = Metric(bottle.Request()).safely_sum([Measurement("4"), Measurement("abc")])
        self.assertEqual(None, measurement)
        self.assertTrue(error_message.startswith("Traceback"))

    def test_safely_sum_with_none(self):
        """Test that None is returned if one of the input measurements is None."""
        measurement, error_message = Metric(bottle.Request()).safely_sum([Measurement("4"), None])
        self.assertEqual(None, measurement)
        self.assertEqual(None, error_message)

    def test_default_target(self):
        """Test that the metric target and default target are included in the response, and are equal by default."""
        measuurement_response = Metric(bottle.Request()).get([Measurement("1")])
        self.assertEqual(Measurement("0"), measuurement_response["default_target"])
        self.assertEqual(Measurement("0"), measuurement_response["target"])

    def test_requested_target(self):
        """Test that the metric target is included in the response, and is equal to the default target by default."""
        request = bottle.Request(dict(QUERY_STRING="target=2"))
        measuurement_response = Metric(request).get(["1"])
        self.assertEqual(Measurement("2"), measuurement_response["target"])

    def test_status_target_met(self):
        """Test the status of a metric that meets the target."""
        measuurement_response = Metric(bottle.Request()).get(["0"])
        self.assertEqual("target_met", measuurement_response["status"])

    def test_status_target_not_met(self):
        """Test the status of a metric that doesn't meet the target."""
        measuurement_response = Metric(bottle.Request()).get(["1"])
        self.assertEqual("target_not_met", measuurement_response["status"])
