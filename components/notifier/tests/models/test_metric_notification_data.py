"""Unit tests for the metric notification data model."""

from shared.model.metric import Metric
from shared.model.report import Report
from shared.model.subject import Subject

from models.metric_notification_data import MetricNotificationData

from tests.fixtures import METRIC_ID, SUBJECT_ID

from .base import DataModelTestCase


class MetricNotificationDataModelTestCase(DataModelTestCase):
    """Unit tests for the metric notification data."""

    def metric(self, name: str | None = "default metric 1", unit: str | None = "unit") -> Metric:
        """Create a metric fixture."""
        metric_data = {"type": "violations", "scale": "count"}
        if name is not None:
            metric_data["name"] = name
        if unit is not None:
            metric_data["unit"] = unit + "s"
            metric_data["unit_singular"] = unit
        return Metric(self.DATA_MODEL, metric_data, METRIC_ID)

    def measurements(self, status: str | None = "target_not_met") -> list:
        """Create measurements fixture."""
        return [
            {"count": {"value": 10, "status": "target_met"}},
            {"count": {"value": 20, "status": status}},
        ]

    def subject(self) -> Subject:
        """Create a subject fixture."""
        report = Report(self.DATA_MODEL, {})
        return Subject(self.DATA_MODEL, {"type": "software", "name": "Subject"}, SUBJECT_ID, report)

    def test_new_status(self):
        """Test that the new status is set correctly."""
        notification_data = MetricNotificationData(self.metric(), METRIC_ID, self.measurements(), self.subject())
        self.assertEqual("target_not_met", notification_data.status)
        self.assertEqual("target not met (red)", notification_data.new_metric_status)

    def test_new_status_for_metric_without_unit(self):
        """Test that the new status is set correctly, even if the metric has no unit."""
        notification_data = MetricNotificationData(
            self.metric(unit=None), METRIC_ID, self.measurements(), self.subject()
        )
        self.assertEqual("target_not_met", notification_data.status)
        self.assertEqual("target not met (red)", notification_data.new_metric_status)

    def test_new_status_for_metric_without_name(self):
        """Test that the new status is set correctly, even if the metric has no name."""
        notification_data = MetricNotificationData(
            self.metric(name=None), METRIC_ID, self.measurements(), self.subject()
        )
        self.assertEqual("target_not_met", notification_data.status)
        self.assertEqual("target not met (red)", notification_data.new_metric_status)

    def test_unknown_status(self):
        """Test that a recent measurement without status works."""
        notification_data = MetricNotificationData(self.metric(), METRIC_ID, self.measurements(None), self.subject())
        self.assertEqual("unknown", notification_data.status)
        self.assertEqual("unknown (white)", notification_data.new_metric_status)

    def test_unknown_status_without_recent_measurements(self):
        """Test that a metric without recent measurements works."""
        notification_data = MetricNotificationData(self.metric(), METRIC_ID, [], self.subject())
        self.assertEqual("unknown", notification_data.status)
        self.assertEqual("unknown (white)", notification_data.new_metric_status)
