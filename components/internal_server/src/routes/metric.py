"""Metric routes."""

from typing import Any

import bottle
from pymongo.database import Database

from database.reports import latest_reports


@bottle.get("/api/metrics")
def get_metrics(database: Database):
    """Get all metrics."""
    metrics: dict[str, Any] = {}
    for report in latest_reports(database):
        issue_tracker = report.get("issue_tracker", {})
        has_issue_tracker = bool(issue_tracker.get("type") and issue_tracker.get("parameters", {}).get("url"))
        for metric in report.metrics:
            metric["report_uuid"] = report["report_uuid"]
            if has_issue_tracker and metric.get("issue_ids"):
                metric["issue_tracker"] = issue_tracker
            metrics[metric.uuid] = metric.summarize([], report_uuid=report.uuid)
    return metrics
