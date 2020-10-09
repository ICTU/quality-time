"""Strategies for notifying users about metrics."""

from typing import List


def reds_per_report(json) -> List:
    """Return the number of red metrics per report in the JSON returned by /api/v3/reports."""
    red_metrics = []
    for report in json["reports"]:
        if "teams_webhook" in report:
            # red_metrics.append([report["report_uuid"], 0, report["teams_webhook"]])
            red_metrics.append({
                "report_uuid": report["report_uuid"],
                "teams_webhook": report["teams_webhook"],
                "red_metrics": 0})
        else:
            # red_metrics.append([report["report_uuid"], 0])
            red_metrics.append({
                "report_uuid": report["report_uuid"],
                "teams_webhook": "",
                "red_metrics": 0})
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if metric["status"] == "target_not_met":
                    red_metrics[-1]["red_metrics"] += 1
    return red_metrics
