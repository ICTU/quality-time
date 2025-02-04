"""Unit tests for the metric notification data model."""

import unittest

from shared.model.metric import Metric

from models.metric_notification_data import MetricNotificationData

from tests.fixtures import METRIC_ID


class MetricNotificationDataModelTestCase(unittest.TestCase):
    """Unit tests for the metric notification data."""

    def setUp(self):
        """Set variables for the other testcases."""
        self.metric = Metric(
            {},
            {
                "type": "metric_type",
                "name": "default metric 1",
                "unit": "units",
                "scale": "count",
            },
            METRIC_ID,
        )
        self.measurements = [
            {"count": {"value": 10, "status": "target_met"}},
            {"count": {"value": 20, "status": "target_not_met"}},
        ]
        self.subject = {"type": "software", "name": "Subject"}

    def test_new_status(self):
        """Test that the new status is set correctly."""
        notification_data = MetricNotificationData(self.metric, METRIC_ID, self.measurements, self.subject)
        self.assertEqual("target_not_met", notification_data.status)
        self.assertEqual("target not met (red)", notification_data.new_metric_status)

    def test_unknown_status(self):
        """Test that a recent measurement without status works."""
        self.measurements[-1]["count"]["status"] = None
        notification_data = MetricNotificationData(self.metric, METRIC_ID, self.measurements, self.subject)
        self.assertEqual("unknown", notification_data.status)
        self.assertEqual("unknown (white)", notification_data.new_metric_status)

    def test_unknown_status_without_recent_measurements(self):
        """Test that a metric without recent measurements works."""
        notification_data = MetricNotificationData(self.metric, METRIC_ID, [], self.subject)
        self.assertEqual("unknown", notification_data.status)
        self.assertEqual("unknown (white)", notification_data.new_metric_status)
