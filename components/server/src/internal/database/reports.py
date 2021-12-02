"""Reports collection."""

import pymongo
from pymongo.database import Database

from model.metric import Metric
from server_utilities.functions import iso_timestamp
from server_utilities.type import MetricId
from .filters import DOES_NOT_EXIST
from .datamodels import latest_datamodel


# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


def latest_reports(database: Database, max_iso_timestamp: str = ""):
    """Return the latest, undeleted, reports in the reports collection."""
    if max_iso_timestamp and max_iso_timestamp < iso_timestamp():
        report_filter = dict(deleted=DOES_NOT_EXIST, timestamp={"$lt": max_iso_timestamp})
        report_uuids = database.reports.distinct("report_uuid", report_filter)
        reports = []
        for report_uuid in report_uuids:
            report_filter["report_uuid"] = report_uuid
            reports.append(database.reports.find_one(report_filter, sort=TIMESTAMP_DESCENDING))
    else:
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
