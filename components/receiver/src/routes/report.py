"""Report routes."""

from typing import Any, Dict

import bottle
from pymongo.database import Database

from database.reports import latest_reports


@bottle.get("/metrics")
def get_metrics(database: Database):
    """Get all metrics."""
    metrics: Dict[str, Any] = {}
    for report in latest_reports(database):
        for subject in report["subjects"].values():
            metrics.update(subject["metrics"])
    return metrics
