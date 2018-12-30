"""Unit tests for the metric class."""

import datetime
import unittest
from unittest.mock import patch

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
        """Test that the metric target and default target are included in the response, and are equal by default."""
        source_response = dict(source=dict(responses=[dict(measurement=Measurement("1"))]))
        measuurement_response = Metric(dict()).get(source_response)
        self.assertEqual(Measurement("0"), measuurement_response["metric"]["default_target"])
        self.assertEqual(Measurement("0"), measuurement_response["measurement"]["target"])

    def test_requested_target(self):
        """Test that the metric target is included in the response, and is equal to the default target by default."""
        source_response = dict(source=dict(responses=[dict(measurement=Measurement("1"))]))
        measuurement_response = Metric(dict(target="2")).get(source_response)
        self.assertEqual(Measurement("2"), measuurement_response["measurement"]["target"])

    def test_status_target_met(self):
        """Test the status of a metric that meets the target."""
        source_response = dict(source=dict(responses=[dict(measurement=Measurement("0"))]))
        measuurement_response = Metric(dict()).get(source_response)
        self.assertEqual("target_met", measuurement_response["measurement"]["status"])

    def test_status_target_not_met(self):
        """Test the status of a metric that doesn't meet the target."""
        source_response = dict(source=dict(responses=[dict(measurement=Measurement("1"))]))
        measuurement_response = Metric(dict()).get(source_response)
        self.assertEqual("target_not_met", measuurement_response["measurement"]["status"])

    def test_timestamp(self):
        """Test that the measurement has a timestamp."""
        source_response = dict(source=dict(responses=[dict(measurement=Measurement("1"))]))
        now = datetime.datetime(2018, 12, 21, 21, 35, 56, 456033)
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = now
            measuurement_response = Metric(dict()).get(source_response)
        self.assertEqual("2018-12-21T21:35:56", measuurement_response["measurement"]["timestamp"])
