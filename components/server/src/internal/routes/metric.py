"""Metric routes."""

from typing import Any

import bottle
from pymongo.database import Database

from database.reports import latest_reports

from ..database.datamodels import latest_datamodel


@bottle.get("/internal-api/v3/metrics", authentication_required=False)
def get_metrics(database: Database):
    """Get all metrics."""
    data_model = latest_datamodel(database)
    metrics: dict[str, Any] = {}
    for report in latest_reports(database, data_model):
        issue_tracker = report.get("issue_tracker", {})
        has_issue_tracker = bool(issue_tracker.get("type") and issue_tracker.get("parameters", {}).get("url"))
        for metric in report.metrics:
            metric["report_uuid"] = report["report_uuid"]
            if has_issue_tracker and metric.get("issue_ids"):
                metric["issue_tracker"] = issue_tracker
            metrics[metric.uuid] = metric.summarize([])
    return metrics
