"""Strategies for notifying users about metrics."""

from typing import List


def reds_per_report(json) -> List:
    """Return the number of red metrics per report in the JSON returned by /api/v3/reports."""
    red_metrics = []
    for report in json["reports"]:
        red_metrics.append([report["report_uuid"], 0])
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if metric["status"] == "target_not_met":
                    red_metrics[-1][1] += 1
    return red_metrics
