"""Strategies for notifying users about metrics."""

from typing import Dict, List, Union


def get_notable_metrics_from_json(
        data_model, json, most_recent_measurement_seen: str) -> List[Dict[str, Union[str, int]]]:
    """Return the reports that have a webhook and metrics that require notifying."""
    notifications = []
    notable_metrics = []
    for report in json["reports"]:
        webhook = report.get("teams_webhook")
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
<<<<<<< HEAD
                if has_new_status(metric, "target_not_met", most_recent_measurement_seen) \
                        or has_new_status(metric, "unknown", most_recent_measurement_seen):
                    notable_metrics.append(create_notification(data_model, metric))
        if webhook and len(notable_metrics) > 0:
=======
                if turned_red(metric, most_recent_measurement_seen) \
                        or turned_white(metric, most_recent_measurement_seen):
                    red_metrics.append(create_notification(data_model, metric))
        if webhook and len(red_metrics) > 0:
>>>>>>> 48c3ba7f... added notification strategy for when metrics turn white
            notifications.append(
                dict(report_uuid=report["report_uuid"], report_title=report["title"], teams_webhook=webhook,
                     url=report.get("url"), metrics=notable_metrics))
    return notifications


def create_notification(data_model, metric):
    """Create the notification dictionary."""
    recent_measurements = metric["recent_measurements"]
    scale = metric["scale"]
    result = dict(
        metric_type=metric["type"],
        metric_name=metric["name"] or f'{data_model["metrics"][metric["type"]]["name"]}',
        metric_unit=metric["unit"] or f'{data_model["metrics"][metric["type"]]["unit"]}',
        new_metric_status=get_status(data_model, recent_measurements[-1][scale]["status"]),
        new_metric_value=recent_measurements[-1][scale]["value"],
        old_metric_status=get_status(data_model, recent_measurements[-2][scale]["status"]),
        old_metric_value=recent_measurements[-2][scale]["value"])
    return result


def get_status(data_model, status) -> str:
    """Get the user friendly status name."""
    statuses = data_model["sources"]["quality_time"]["parameters"]["status"]["api_values"]
    # The statuses have the human readable version of the status as key and the status itself as value so we need to
    # invert the dictionary:
    inverted_statuses = {statuses[key]: key for key in statuses}
    human_readable_status, color = str(inverted_statuses[status]).strip(")").split(" (")
    return f"{color} ({human_readable_status})"


<<<<<<< HEAD
def has_new_status(metric, new_status: str, most_recent_measurement_seen: str) -> bool:
    """Determine if a metric got a new status after the timestamp of the most recent measurement seen."""
    recent_measurements = metric.get("recent_measurements") or []
    if len(recent_measurements) < 2:
        return False  # If there are fewer than two measurements, the metric didn't recently change status
    metric_has_status = metric["status"] == new_status
    scale = metric["scale"]
    metric_had_other_status = recent_measurements[-2][scale]["status"] != new_status
    change_was_recent = recent_measurements[-1]["start"] > most_recent_measurement_seen
    return bool(metric_has_status and metric_had_other_status and change_was_recent)
=======
def turned_red(metric, most_recent_measurement_seen: str) -> bool:
    """Determine if a metric turned red after the timestamp of the most recent measurement seen."""
    metric_is_red = metric["status"] == "target_not_met"
    recent_measurements = metric.get("recent_measurements")
    return bool(
        metric_is_red and recent_measurements and recent_measurements[-1]["start"] > most_recent_measurement_seen)

def turned_white(metric, most_recent_measurement_seen: str)-> bool:
    """Determine if a metric turned white after the timestamp of the most recent measurement seen."""
    scale = metric["scale"]
    metric_is_white = metric["status"] == "unknown"
    recent_measurements = metric.get("recent_measurements")
    if recent_measurements and len(recent_measurements) > 1:
        metric_was_not_white = recent_measurements[-2][scale]["status"] != "unknown"
        return bool(
            metric_is_white and metric_was_not_white and
            recent_measurements[-1]["start"] > most_recent_measurement_seen)
    return False
>>>>>>> 48c3ba7f... added notification strategy for when metrics turn white
