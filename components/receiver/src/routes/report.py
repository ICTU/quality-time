"""Report routes."""

from typing import Any, Dict

import bottle
from pymongo.database import Database

from database.reports import latest_reports
from utilities.functions import report_date_time


@bottle.get("/metrics")
def get_metrics(database: Database):
    """Get all metrics."""
    metrics: Dict[str, Any] = {}
    for report in latest_reports(database, report_date_time()):
        for subject in report["subjects"].values():
            metrics.update(subject["metrics"])
    return metrics
