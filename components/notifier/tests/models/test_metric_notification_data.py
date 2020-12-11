"""Unit tests for the metric notification data model."""

import unittest

from models.metric_notification_data import MetricNotificationData


class MetricNotificationDataModelTestCase(unittest.TestCase):
    """Unit tests for the metric notification data."""

    def setUp(self):
        """Set variables for the other testcases."""
        self.data_model = dict(metrics=dict(metric_type=dict(name="type")),
                               sources=dict(quality_time=dict(parameters=dict(status=dict(api_values={
                                   "target met (green)": "target_met",
                                   "target not met (red)": "target_not_met",
                               })))))
        self.metric1 = dict(
            type="metric_type",
            name="default metric 1",
            unit="units",
            scale="count",
            recent_measurements=[dict(count=dict(value=10,
                                                 status="target_met")),
                                 dict(count=dict(value=20,
                                                 status="target_not_met"))])

    def test_initialisation(self):
        """test that an object can be initialised."""
        MetricNotificationData(self.metric1, self.data_model)
