"""Strategies for notifying users about metrics."""

from datetime import datetime, timedelta
from typing import Optional

from models.notification import Notification
from models.metric_notification_data import MetricNotificationData


class NotificationFinder:
    """Handle notification contents and status."""

    def __init__(self, data_model):
        """Initialise already notified list and store data model."""
        self.already_notified = []
        self.data_model = data_model

    def get_notifications(self, json, most_recent_measurement_seen: datetime) -> list[Notification]:
        """Return the reports that have a webhook and metrics that require notifying."""
        notifications = []
        for report in json["reports"]:
            notable_metrics = []
            for subject in report["subjects"].values():
                for metric_uuid, metric in subject["metrics"].items():
                    notable = self.get_notification(metric, metric_uuid, most_recent_measurement_seen)
                    if notable:
                        notable_metrics.append(MetricNotificationData(metric, subject, self.data_model, notable))
            if notable_metrics:
                for destination_uuid, destination in report.get("notification_destinations", {}).items():
                    notifications.append(Notification(report, notable_metrics, destination_uuid, destination))
        return notifications

    def get_notification(self, metric, metric_uuid, most_recent_measurement_seen: datetime) -> Optional[str]:
        """Determine whether a notification should be generated for the given metric."""
        if (
            len(metric["recent_measurements"]) > 0
            and metric.get("status_start")
            and self.__long_unchanged_status(metric, metric_uuid, most_recent_measurement_seen)
        ):
            return "status_long_unchanged"
        if self.status_changed(metric, most_recent_measurement_seen):
            if metric_uuid in self.already_notified:
                self.already_notified.remove(metric_uuid)
            return "status_changed"
        return None

    @staticmethod
    def status_changed(metric, most_recent_measurement_seen: datetime) -> bool:
        """Determine if a metric got a new status after the given timestamp."""
        recent_measurements = metric.get("recent_measurements") or []
        if len(recent_measurements) < 2:
            return False  # If there are fewer than two measurements, the metric couldn't have recently changed status
        scale = metric["scale"]
        metric_had_other_status = recent_measurements[-2][scale]["status"] != recent_measurements[-1][scale]["status"]
        change_was_recent = datetime.fromisoformat(recent_measurements[-1]["start"]) > most_recent_measurement_seen
        return bool(metric_had_other_status and change_was_recent)

    def __long_unchanged_status(self, metric, metric_uuid, most_recent_measurement_seen: datetime) -> bool:
        """Determine if a metric has had the same status for 3 weeks."""
        status_start = datetime.fromisoformat(metric["status_start"])
        difference = most_recent_measurement_seen - status_start
        if timedelta(days=21) < difference < timedelta(days=22) and metric_uuid not in self.already_notified:
            self.already_notified.append(metric_uuid)
            return True
        return False
