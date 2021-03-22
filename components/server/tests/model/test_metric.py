"""Unit tests for the Metric model class."""

import unittest

from model.metric import Metric

from ..fixtures import METRIC_ID


class MetricStatusTest(unittest.TestCase):
    """Unit tests for determining the metric status, given a measurement value."""

    def setUp(self):
        """Override to set up the data model."""
        self.data_model = dict(metrics=dict(metric_type=dict(direction="<")))

    def metric(self, **metric_data) -> Metric:
        """Create a metric fixture."""
        return Metric(self.data_model, dict(type="metric_type", **metric_data), METRIC_ID)

    def test_green(self):
        """Test a green measurement."""
        metric = self.metric(target="20", near_target="15")
        self.assertEqual("target_met", metric.status("10"))

    def test_yellow(self):
        """Test a yellow measurement."""
        metric = self.metric(target="20", near_target="25")
        self.assertEqual("near_target_met", metric.status("22"))

    def test_red(self):
        """Test a red measurement."""
        metric = self.metric(target="20", near_target="25")
        self.assertEqual("target_not_met", metric.status("30"))

    def test_debt_met(self):
        """Test a measurement better than the accepted debt."""
        metric = self.metric(target="20", near_target="25", debt_target="30", accept_debt=True)
        self.assertEqual("debt_target_met", metric.status("30"))

    def test_debt_not_met(self):
        """Test a measurement worse than the accepted debt."""
        metric = self.metric(target="20", near_target="25", debt_target="30", accept_debt=True)
        self.assertEqual("target_not_met", metric.status("35"))

    def test_debt_past_end_date(self):
        """Test a measurement with expired debt."""
        metric = self.metric(
            target="20", near_target="25", debt_target="30", accept_debt=True, debt_end_date="2019-06-10"
        )
        self.assertEqual("target_not_met", metric.status("29"))

    def test_debt_end_date_removed(self):
        """Test a measurement with the technical end date reset."""
        metric = self.metric(target="20", near_target="25", debt_target="30", accept_debt=True, debt_end_date="")
        self.assertEqual("debt_target_met", metric.status("29"))

    def test_green_with_debt(self):
        """Test a measurement with debt, better than the target."""
        metric = self.metric(target="20", near_target="25", debt_target="30", accept_debt=True)
        self.assertEqual("target_met", metric.status("15"))

    def test_near_target_worse_than_target(self):
        """Test that the measurement is red when the near target is worse than the target."""
        metric = self.metric(target="20", near_target="15")
        self.assertEqual("target_met", metric.status("17"))
