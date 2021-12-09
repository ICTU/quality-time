"""Reports collection."""

import pymongo
from pymongo.database import Database

from internal.model.metric import Metric
from internal.server_utilities.type import MetricId
from .filters import DOES_NOT_EXIST
from .datamodels import latest_datamodel


# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


def latest_reports(database: Database):
    """Return the latest, undeleted, reports in the reports collection."""
    reports = list(database.reports.find({"last": True, "deleted": DOES_NOT_EXIST}))
    for report in reports:
        report["_id"] = str(report["_id"])
    return reports


def latest_metric(database: Database, metric_uuid: MetricId) -> Metric | None:
    """Return the latest metric with the specified metric uuid."""
    for report in latest_reports(database):
        for subject in report.get("subjects", {}).values():
            metrics = subject.get("metrics", {})
            if metric_uuid in metrics:
                return Metric(latest_datamodel(database), metrics[metric_uuid], metric_uuid)
    return None
