"""Strategies for notifying users about metrics."""

from datetime import datetime

from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.model.report import Report

from models.metric_notification_data import MetricNotificationData, NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS_CHANGE
from models.notification import Notification


class NotificationFinder:
    """Handle notification contents and status."""

    def get_notifications(
        self,
        reports: list[Report],
        measurements: list[Measurement],
        most_recent_measurement_seen: datetime,
    ) -> list[Notification]:
        """Return the reports that have a webhook and metrics that require notifying."""
        measurements.sort(key=lambda measurement: str(measurement["end"]))  # Sort ascending by end timestamp
        notifications = []
        for report in reports:
            notable_metrics = []
            for subject in report["subjects"].values():
                for metric_uuid, metric in subject["metrics"].items():
                    metric_measurements = [m for m in measurements if m["metric_uuid"] == metric_uuid]
                    if self.status_changed(metric, metric_measurements, most_recent_measurement_seen):
                        notable_metrics.append(MetricNotificationData(metric, metric_measurements, subject))
            if notable_metrics:
                for destination_uuid, destination in report.get("notification_destinations", {}).items():
                    notifications.append(Notification(report, notable_metrics, destination_uuid, destination))
        return notifications

    @staticmethod
    def status_changed(metric: Metric, measurements: list[Measurement], most_recent_measurement_seen: datetime) -> bool:
        """Determine if a metric got a new status after the given timestamp."""
        if len(measurements) < NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS_CHANGE:
            return False
        scale = metric["scale"]
        metric_had_other_status = measurements[-2][scale]["status"] != measurements[-1][scale]["status"]
        change_was_recent = datetime.fromisoformat(measurements[-1]["start"]) > most_recent_measurement_seen
        return bool(metric_had_other_status and change_was_recent)
