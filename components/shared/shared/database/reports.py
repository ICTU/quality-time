"""Reports collection."""

import pymongo
from pymongo.database import Database


def latest_metric(database: Database, report_uuid: str, metric_uuid: str):
    """Return the latest metric with the specified report and metric uuid."""
    report = latest_report(database, report_uuid) or dict()
    for subject in report.get("subjects", {}).values():
        metrics = subject.get("metrics", {})
        if metric_uuid in metrics:
            return metrics[metric_uuid]
    return None


def latest_report(database: Database, report_uuid: str):
    """Return the latest report for the specified report uuid."""
    return database.reports.find_one(filter={"report_uuid": report_uuid}, sort=[("timestamp", pymongo.DESCENDING)])
