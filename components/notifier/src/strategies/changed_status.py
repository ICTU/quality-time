"""Strategies for notifying users about metrics."""

from typing import List
from models.notification import Notification
from models.metric_notification_data import MetricNotificationData


def get_notable_metrics_from_json(data_model, json, most_recent_measurement_seen: str) -> List[Notification]:
    """Return the reports that have a webhook and metrics that require notifying."""
    notifications = []
    for report in json["reports"]:
        notable_metrics = []
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if status_changed(metric, most_recent_measurement_seen):
                    notable_metrics.append(MetricNotificationData(metric, data_model))
        if notable_metrics:
            for destination_uuid, destination in report.get("notification_destinations", {}).items():
                notifications.append(Notification(report, notable_metrics, destination_uuid, destination))
    return notifications


def status_changed(metric, most_recent_measurement_seen: str) -> bool:
    """Determine if a metric got a new status after the given timestamp."""
    recent_measurements = metric.get("recent_measurements") or []
    if len(recent_measurements) < 2:
        return False  # If there are fewer than two measurements, the metric couldn't have recently changed status
    scale = metric["scale"]
    metric_had_other_status = recent_measurements[-2][scale]["status"] != recent_measurements[-1][scale]["status"]
    change_was_recent = recent_measurements[-1]["start"] > most_recent_measurement_seen
    return bool(metric_had_other_status and change_was_recent)
