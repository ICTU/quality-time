"""Strategies for notifying users about metrics."""

from typing import Dict, List, Union


def reds_that_are_new(json, most_recent_measurement_seen: str) -> List[Dict[str, Union[str, int]]]:
    """Return the reports that have a webhook and new red metrics."""
    notifications = []
    for report in json["reports"]:
        webhook = report.get("teams_webhook")
        nr_red = 0
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if turned_red(metric, most_recent_measurement_seen):
                    nr_red += 1
        if webhook and nr_red > 0:
            notifications.append(
                dict(report_uuid=report["report_uuid"], report_title=report["title"], teams_webhook=webhook,
                     url=report.get("url", ""), new_red_metrics=nr_red))
    return notifications


def turned_red(metric, most_recent_measurement_seen: str) -> bool:
    """Determine if a metric turned red after the timestamp of the most recent measurement seen."""
    metric_is_red = metric["status"] == "target_not_met"
    recent_measurements = metric.get("recent_measurements")
    return bool(
        metric_is_red and recent_measurements and recent_measurements[-1]["start"] > most_recent_measurement_seen)
