"""Unit tests for the metric notification data model."""

import unittest

from models.metric_notification_data import MetricNotificationData


class MetricNotificationDataModelTestCase(unittest.TestCase):
    """Unit tests for the metric notification data."""

    def setUp(self):
        """Set variables for the other testcases."""
        self.data_model = dict(
            metrics=dict(metric_type=dict(name="type")),
            sources=dict(
                quality_time=dict(
                    parameters=dict(
                        status=dict(
                            api_values={
                                "target met (green)": "target_met",
                                "target not met (red)": "target_not_met",
                            }
                        )
                    )
                )
            ),
        )
        self.metric = dict(
            type="metric_type",
            name="default metric 1",
            unit="units",
            scale="count",
            recent_measurements=[
                dict(count=dict(value=10, status="target_met")),
                dict(count=dict(value=20, status="target_not_met")),
            ],
        )
        self.subject = dict(type="software", name="Subject")

    def test_new_status(self):
        """Test that the new status is set correctly."""
        new_status = MetricNotificationData(
            self.metric, self.subject, self.data_model, "status_changed"
        ).new_metric_status
        self.assertEqual("red (target not met)", new_status)

    def test_unknown_status(self):
        """Test that a recent measurement without status works."""
        self.metric["recent_measurements"][-1]["count"]["status"] = None
        new_status = MetricNotificationData(
            self.metric, self.subject, self.data_model, "status_changed"
        ).new_metric_status
        self.assertEqual("white (unknown)", new_status)

    def test_unknown_status_without_recent_measurements(self):
        """Test that a metric without recent measurements works."""
        self.metric["recent_measurements"] = []
        new_status = MetricNotificationData(
            self.metric, self.subject, self.data_model, "status_changed"
        ).new_metric_status
        self.assertEqual("white (unknown)", new_status)
