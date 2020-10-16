"""Strategies for notifying users about metrics."""

from typing import List


def reds_that_are_new(json) -> List:
    """Return the number of red metrics per report in the JSON returned by /api/v3/reports."""
    new_red_metrics = []
    for report in json["reports"]:
        new_red_metrics.append({
            "report_uuid": report["report_uuid"],
            "report_title": report["title"],
            "teams_webhook": report.get("teams_webhook", ""),
            "url": report.get("url", ""),
            "new_red_metrics": 0})
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if metric["status"] == "target_not_met":
                    if used_to_be_not_red(metric):
                        new_red_metrics[-1]["new_red_metrics"] += 1

    return new_red_metrics


def used_to_be_not_red(metric):
    if "recent_measurements" in metric:
        if metric["recent_measurements"][0]["count"]["status"] != "target_not_met":
            return True
        else:
            return False
    else:
        return True
