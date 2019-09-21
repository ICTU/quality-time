"""Test the measurements collection."""

import unittest
from unittest import mock

from src.database.measurements import calculate_measurement_value, determine_measurement_status


class DetermineMeasurementStatusTest(unittest.TestCase):
    """Unit tests for determining the measurement status."""

    def setUp(self):
        self.database = mock.Mock()
        self.database.datamodels.find_one = mock.Mock(
            return_value=dict(_id="", metrics=dict(metric_type=dict(direction="<"))))

    def test_green(self):
        """Test a green measurement."""
        metric = dict(type="metric_type", target="20", near_target="15", debt_target=None, accept_debt=False)
        self.assertEqual(
            "target_met", determine_measurement_status(self.database, metric, "10"))

    def test_yellow(self):
        """Test a yellow measurement."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target=None, accept_debt=False)
        self.assertEqual(
            "near_target_met", determine_measurement_status(self.database, metric, "22"))

    def test_red(self):
        """Test a red measurement."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target=None, accept_debt=False)
        self.assertEqual(
            "target_not_met", determine_measurement_status(self.database, metric, "30"))

    def test_debt_met(self):
        """Test a measurement better than the accepted debt."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target="30", accept_debt=True)
        self.assertEqual(
            "debt_target_met", determine_measurement_status(self.database, metric, "30"))

    def test_debt_not_met(self):
        """Test a measurement worse than the accepted debt."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target="30", accept_debt=True)
        self.assertEqual(
            "target_not_met", determine_measurement_status(self.database, metric, "35"))

    def test_debt_past_end_date(self):
        """Test a measurement with experide debt."""
        metric = dict(
            type="metric_type", target="20", near_target="25", debt_target="30", accept_debt=True,
            debt_end_date="2019-06-10")
        self.assertEqual(
            "target_not_met", determine_measurement_status(self.database, metric, "29"))

    def test_green_with_debt(self):
        """Test a measurement with debt, better than the target."""
        metric = dict(type="metric_type", target="20", near_target="25", debt_target="30", accept_debt=True)
        self.assertEqual(
            "target_met", determine_measurement_status(self.database, metric, "15"))

    def test_near_target_worse_than_target(self):
        """Test that the measurement is red when the near target is worse than the target."""
        metric = dict(type="metric_type", target="20", near_target="15", debt_target=None, accept_debt=False)
        self.assertEqual(
            "target_met", determine_measurement_status(self.database, metric, "17"))


class CalculateMeasurementValueTest(unittest.TestCase):
    """Unit tests for calculating the measurement value from one or more source measurements."""

    def test_no_source_measurements(self):
        """Test that the measurement value is None if there are no sources."""
        self.assertEqual(None, calculate_measurement_value([], "sum", "count", "<"))

    def test_error(self):
        """Test that the measurement value is None if a source has an erro."""
        sources = [dict(parse_error="error")]
        self.assertEqual(None, calculate_measurement_value(sources, "sum", "count", "<"))

    def test_add_two_sources(self):
        """Test that the values of two sources are added."""
        sources = [dict(parse_error=None, connection_error=None, value="10", total=None),
                   dict(parse_error=None, connection_error=None, value="20", total=None)]
        self.assertEqual("30", calculate_measurement_value(sources, "sum", "count", "<"))

    def test_max_two_sources(self):
        """Test that the max value of two sources is returned."""
        sources = [dict(parse_error=None, connection_error=None, value="10", total=None),
                   dict(parse_error=None, connection_error=None, value="20", total=None)]
        self.assertEqual("20", calculate_measurement_value(sources, "max", "count", "<"))

    def test_ignored_entities(self):
        """Test that the number of ignored entities is subtracted."""
        sources = [
            dict(parse_error=None, connection_error=None, value="10", total=None,
                 entity_user_data=dict(
                     entity1=dict(status="fixed"), entity2=dict(status="wont_fix"),
                     entity3=dict(status="false_positive")))]
        self.assertEqual("7", calculate_measurement_value(sources, "sum", "count", "<"))

    def test_percentage(self):
        """Test a non-zero percentage."""
        sources = [dict(parse_error=None, connection_error=None, value="10", total="70"),
                   dict(parse_error=None, connection_error=None, value="20", total="50")]
        self.assertEqual("25", calculate_measurement_value(sources, "sum", "percentage", "<"))

    def test_percentage_is_zero(self):
        """Test that the percentage is zero when the total is zero and the direction is 'fewer is better'."""
        sources = [dict(parse_error=None, connection_error=None, value="0", total="0")]
        self.assertEqual("0", calculate_measurement_value(sources, "sum", "percentage", "<"))

    def test_percentage_is_100(self):
        """Test that the percentage is 100 when the total is zero and the direction is 'more is better'."""
        sources = [dict(parse_error=None, connection_error=None, value="0", total="0")]
        self.assertEqual("100", calculate_measurement_value(sources, "sum", "percentage", ">"))

    def test_min_of_percentages(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        sources = [dict(parse_error=None, connection_error=None, value="10", total="70"),
                   dict(parse_error=None, connection_error=None, value="20", total="50")]
        self.assertEqual("14", calculate_measurement_value(sources, "min", "percentage", "<"))

    def test_min_of_percentages_with_zero_denominator(self):
        """Test that the value is the minimum of the percentages when the scale is percentage and addition is min."""
        sources = [dict(parse_error=None, connection_error=None, value="10", total="70"),
                   dict(parse_error=None, connection_error=None, value="0", total="0")]
        self.assertEqual("0", calculate_measurement_value(sources, "min", "percentage", "<"))
