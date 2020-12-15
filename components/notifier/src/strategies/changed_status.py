"""Strategies for notifying users about metrics."""

from datetime import datetime, timedelta
from typing import List, Optional
from models.notification import Notification
from models.metric_notification_data import MetricNotificationData


def get_notable_metrics_from_json(data_model, json, most_recent_measurement_seen: str) -> List[Notification]:
    """Return the reports that have a webhook and metrics that require notifying."""
    notifications = []
    for report in json["reports"]:
        notable_metrics = []
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                notable = check_if_metric_is_notable(metric, most_recent_measurement_seen)
                if notable:
                    notable_metrics.append(MetricNotificationData(metric, data_model, notable))
        if notable_metrics:
            for destination_uuid, destination in report.get("notification_destinations", {}).items():
                notifications.append(Notification(report, notable_metrics, destination_uuid, destination))
    return notifications


def check_if_metric_is_notable(metric, most_recent_measurement_seen) -> Optional[str]:
    """Determine whether a notification should be generated for the given metric."""
    if len(metric["recent_measurements"]) > 0 and "status_start" in metric["recent_measurements"][-1][metric["scale"]]:
        if long_red(metric, most_recent_measurement_seen):
            return "long_red"
    if status_changed(metric, most_recent_measurement_seen):
        return "status_changed"
    return None


def status_changed(metric, most_recent_measurement_seen: str) -> bool:
    """Determine if a metric got a new status after the given timestamp."""
    recent_measurements = metric.get("recent_measurements") or []
    if len(recent_measurements) < 2:
        return False  # If there are fewer than two measurements, the metric couldn't have recently changed status
    scale = metric["scale"]
    metric_had_other_status = recent_measurements[-2][scale]["status"] != recent_measurements[-1][scale]["status"]
    change_was_recent = recent_measurements[-1]["start"] > most_recent_measurement_seen
    return bool(metric_had_other_status and change_was_recent)


def long_red(metric, most_recent_measurement_seen: str) -> bool:
    """Determine if a metric has been red for 3 weeks."""
    status_start = datetime.fromisoformat(metric["recent_measurements"][-1][metric["scale"]]["status_start"])
    datetime_most_recent_measurement_seen = datetime.fromisoformat(most_recent_measurement_seen)
    difference = datetime_most_recent_measurement_seen - status_start
    return difference.total_seconds() / 60.0 > timedelta(days=21).total_seconds() / 60.0