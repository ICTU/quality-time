from typing import List


def reds_per_report(json, log_level: int = None) -> List:
    red_metrics = []
    for report in json["reports"]:
        red_metrics.append([report["report_uuid"], 0])
        print(report["report_uuid"])
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                print(metric["status"], flush=True)
                if metric["status"] == "target_not_met":
                    red_metrics[-1][1] += 1
    return red_metrics
