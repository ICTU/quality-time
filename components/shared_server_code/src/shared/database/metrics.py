"""Module for shared metric methods"""

from shared.model.metric import Metric
from shared.model.report import Report
from shared.utils.type import MetricId


def get_metrics_from_reports(reports: list[Report]) -> dict[MetricId, Metric]:
    """Return the metrics from the reports."""
    metrics: dict[MetricId, Metric] = {}

    for report in reports:
        metrics_dict: dict[MetricId, Metric] = report.metrics_dict.copy()
        for metric in metrics_dict.values():
            metric["report_uuid"] = report["report_uuid"]
        metrics.update(metrics_dict)
    return metrics
