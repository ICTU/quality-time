from typing import List


def reds_per_report(json) -> List:
    red_metrics = []
    for report in json["reports"]:
        red_metrics.append([report["report_uuid"], 0])
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if metric["status"] == "target_not_met":
                    red_metrics[-1][1] += 1
    return red_metrics
