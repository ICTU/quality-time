"""Strategies for notifying users about metrics."""

from typing import Dict, List, Union


def get_notable_metrics_from_json(json, most_recent_measurement_seen: str) -> List[Dict[str, Union[str, int]]]:
    """Return the reports that have a webhook and metrics that require notifying."""
    notifications = []
    red_metrics = []
    for report in json["reports"]:
        webhook = report.get("teams_webhook")
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if turned_red(metric, most_recent_measurement_seen):
                    red_metrics.append(create_metric(metric))
        if webhook and len(red_metrics) > 0:
            notifications.append(
                dict(report_uuid=report["report_uuid"], report_title=report["title"], teams_webhook=webhook,
                     url=report.get("url"), new_red_metrics=len(red_metrics), metrics=red_metrics))
    return notifications

def create_metric(metric):
    result = dict(
        metric_type=metric["type"],
        metric_name=metric["name"],
        metric_unit=metric["unit"],
        new_metric_status=metric["recent_measurements"][-1]["count"]["status"],
        new_metric_value=metric["recent_measurements"][-1]["count"]["value"]
    )
    if len(metric["recent_measurements"]) > 1:
        result["old_metric_status"] = metric["recent_measurements"][-2]["count"]["status"]
        result["old_metric_value"] = metric["recent_measurements"][-2]["count"]["value"]
    return result

def turned_red(metric, most_recent_measurement_seen: str) -> bool:
    """Determine if a metric turned red after the timestamp of the most recent measurement seen."""
    metric_is_red = metric["status"] == "target_not_met"
    recent_measurements = metric.get("recent_measurements")
    return bool(
        metric_is_red and recent_measurements and recent_measurements[-1]["start"] > most_recent_measurement_seen)
