"""Reports collection."""

from typing import Dict

import pymongo
from pymongo.database import Database

from utilities.functions import iso_timestamp
from .datamodels import latest_datamodel


def latest_reports(database: Database, max_iso_timestamp: str = ""):
    """Return all latest reports in the reports collection."""
    report_uuids = database.reports.distinct("report_uuid")
    reports = []
    for report_uuid in report_uuids:
        report = database.reports.find_one(
            filter={"report_uuid": report_uuid, "timestamp": {"$lt": max_iso_timestamp or iso_timestamp()}},
            sort=[("timestamp", pymongo.DESCENDING)])
        if report and "deleted" not in report:
            report["_id"] = str(report["_id"])
            # Include a summary of the current measurement values
            summarize_report(database, report)
            reports.append(report)
    return reports


def latest_reports_overview(database: Database, max_iso_timestamp: str = "") -> Dict:
    """Return the latest reports overview."""
    overview = database.reports_overviews.find_one(
        filter={"timestamp": {"$lt": max_iso_timestamp or iso_timestamp()}}, sort=[("timestamp", pymongo.DESCENDING)])
    if overview:
        overview["_id"] = str(overview["_id"])
    return overview or dict()


def summarize_report(database: Database, report) -> None:
    """Add a summary of the measurements to each subject."""
    from .measurements import last_measurements  # pylint:disable=cyclic-import
    status_color_mapping = dict(
        target_met="green", debt_target_met="grey", near_target_met="yellow", target_not_met="red")
    report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=0)
    report["summary_by_subject"] = dict()
    report["summary_by_tag"] = dict()
    last_measurements_by_metric_uuid = {m["metric_uuid"]: m for m in last_measurements(database, report["report_uuid"])}
    datamodel = latest_datamodel(database)
    for subject_uuid, subject in report.get("subjects", {}).items():
        for metric_uuid, metric in subject.get("metrics", {}).items():
            last_measurement = last_measurements_by_metric_uuid.get(metric_uuid, dict())
            scale = metric.get("scale") or datamodel["metrics"][metric["type"]].get("default_scale", "count")
            status = last_measurement.get(scale, {}).get("status", last_measurement.get("status", None))
            color = status_color_mapping.get(status, "white")
            report["summary"][color] += 1
            report["summary_by_subject"].setdefault(
                subject_uuid, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1
            for tag in metric["tags"]:
                report["summary_by_tag"].setdefault(tag, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1


def latest_report(database: Database, report_uuid: str):
    """Return the latest report for the specified report uuid."""
    return database.reports.find_one(filter={"report_uuid": report_uuid}, sort=[("timestamp", pymongo.DESCENDING)])


def latest_metric(database: Database, report_uuid: str, metric_uuid: str):
    """Return the latest metric with the specified report and metric uuid."""
    report = latest_report(database, report_uuid) or dict()
    for subject in report.get("subjects", {}).values():
        metrics = subject.get("metrics", {})
        if metric_uuid in metrics:
            return metrics[metric_uuid]
    return None


def insert_new_report(database: Database, report):
    """Insert a new report in the reports collection."""
    if "_id" in report:
        del report["_id"]
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)
    return dict(ok=True)


def insert_new_reports_overview(database: Database, reports_overview):
    """Insert a new reports overview in the reports overview collection."""
    if "_id" in reports_overview:
        del reports_overview["_id"]
    reports_overview["timestamp"] = iso_timestamp()
    database.reports_overviews.insert(reports_overview)
    return dict(ok=True)


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog for the report, narrowed to a single subject, metric, or source if so required.
    The uuids keyword arguments should contain report_uuid="report_uuid" and optionally subject_uuid="subject_uuid",
    metric_uuid="metric_uuid", and source_uuid="source_uuid"."""
    # Build a filter for finding the right "delta" subdocuments using the passed uuid's
    delta_filter = {f"delta.{key}": value for key, value in uuids.items() if value}
    # Find the "nr_changes" most recent "delta" subdocuments with the required uuid's and return (using the projection)
    # the description and the timestamp of the report:
    return database.reports.find(
        filter=delta_filter, sort=[("timestamp", pymongo.DESCENDING)], limit=nr_changes,
        projection={"delta.description": True, "timestamp": True})
