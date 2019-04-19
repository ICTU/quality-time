"""Test the measurements collection."""

import unittest
from unittest import mock

from src.database.measurements import determine_measurement_status


class DetermineMeasurementStatusTest(unittest.TestCase):
    """Unit tests for determining the measurement status."""

    def setUp(self):
        self.database = mock.Mock()
        self.database.datamodels.find_one = mock.Mock(
            return_value=dict(_id="", metrics=dict(metric_type=dict(direction="<="))))

    def test_green(self):
        """Test a green measurement."""
        metric = dict(type="metric_type", target="20", near_target="15", debt_target=None)
        self.assertEqual(
            "target_met", determine_measurement_status(self.database, metric, "10", None, None, None, None))

    def test_yellow(self):
        """Test a yellow measurement."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target=None)
        self.assertEqual(
            "near_target_met", determine_measurement_status(self.database, metric, "22", None, None, None, None))

    def test_red(self):
        """Test a red measurement."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target=None)
        self.assertEqual(
            "target_not_met", determine_measurement_status(self.database, metric, "30", None, None, None, None))

    def test_debt_met(self):
        """Test a measurement better than the accepted debt."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target="30")
        self.assertEqual(
            "debt_target_met", determine_measurement_status(self.database, metric, "30", None, None, None, True))

    def test_debt_not_met(self):
        """Test a measurement worse than the accepted debt."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target="30")
        self.assertEqual(
            "target_not_met", determine_measurement_status(self.database, metric, "35", None, None, None, True))

    def test_green_with_debt(self):
        """Test a measurement with debt, better than the target."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target="30")
        self.assertEqual(
            "target_met", determine_measurement_status(self.database, metric, "15", None, None, None, True))

    def test_near_target_worse_than_target(self):
        """Test that the measurement is red when the near target is worse than the target."""
        metric = dict(type="metric_type", target="20", near_target="15", debt_target=None)
        self.assertEqual(
            "target_met", determine_measurement_status(self.database, metric, "17", None, None, None, None))
