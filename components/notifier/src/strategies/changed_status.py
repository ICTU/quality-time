"""Strategies for notifying users about metrics."""

from typing import Dict, List
from notification import Notification


def get_notable_metrics_from_json(data_model, json, most_recent_measurement_seen: str) -> List[Notification]:
    """Return the reports that have a webhook and metrics that require notifying."""
    notifications = []
    for report in json["reports"]:
        notable_metrics = []
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if has_new_status(metric, most_recent_measurement_seen, "target_not_met", "unknown"):
                    notable_metrics.append(create_notification(data_model, metric))
        if notable_metrics:
            for destination_uuid, destination in report.get("notification_destinations", {}).items():
                notifications.append(Notification(report, notable_metrics, destination_uuid, destination))
    return notifications


def create_notification(data_model, metric) -> Dict[str, str]:
    """Create the notification dictionary."""
    recent_measurements = metric["recent_measurements"]
    scale = metric["scale"]
    return dict(
        metric_type=metric["type"],
        metric_name=metric["name"] or f'{data_model["metrics"][metric["type"]]["name"]}',
        metric_unit=metric["unit"] or f'{data_model["metrics"][metric["type"]]["unit"]}',
        new_metric_status=get_status(data_model, recent_measurements[-1][scale]["status"]),
        new_metric_value=recent_measurements[-1][scale]["value"],
        old_metric_status=get_status(data_model, recent_measurements[-2][scale]["status"]),
        old_metric_value=recent_measurements[-2][scale]["value"],
    )


def get_status(data_model, status) -> str:
    """Get the user friendly status name."""
    statuses = data_model["sources"]["quality_time"]["parameters"]["status"]["api_values"]
    # The statuses have the human readable version of the status as key and the status itself as value so we need to
    # invert the dictionary:
    inverted_statuses = {statuses[key]: key for key in statuses}
    human_readable_status, color = str(inverted_statuses[status]).strip(")").split(" (")
    return f"{color} ({human_readable_status})"


def has_new_status(metric, most_recent_measurement_seen: str, *new_statuses: str) -> bool:
    """Determine if a metric got a new status after the timestamp of the most recent measurement seen."""
    recent_measurements = metric.get("recent_measurements") or []
    if len(recent_measurements) < 2:
        return False  # If there are fewer than two measurements, the metric didn't recently change status
    metric_has_status = metric["status"] in new_statuses
    scale = metric["scale"]
    metric_had_other_status = recent_measurements[-2][scale]["status"] != metric["status"]
    change_was_recent = recent_measurements[-1]["start"] > most_recent_measurement_seen
    return bool(metric_has_status and metric_had_other_status and change_was_recent)
