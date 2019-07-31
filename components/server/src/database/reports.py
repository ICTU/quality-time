"""Reports collection."""

from typing import Dict

import pymongo
from pymongo.database import Database
from shared.utilities.functions import iso_timestamp

from utilities.type import Summary


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
    summary = dict(red=0, green=0, yellow=0, grey=0, white=0)
    summary_by_subject: Dict[str, Summary] = dict()
    summary_by_tag: Dict[str, Summary] = dict()
    last_measurements_by_metric_uuid = {m["metric_uuid"]: m for m in last_measurements(database, report["report_uuid"])}
    for subject_uuid, subject in report.get("subjects", {}).items():
        for metric_uuid, metric in subject.get("metrics", {}).items():
            last_measurement = last_measurements_by_metric_uuid.get(metric_uuid)
            color = status_color_mapping.get(last_measurement["status"], "white") if last_measurement else "white"
            summary[color] += 1
            summary_by_subject.setdefault(subject_uuid, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1
            for tag in metric["tags"]:
                summary_by_tag.setdefault(tag, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1
    report["summary"] = summary
    report["summary_by_subject"] = summary_by_subject
    report["summary_by_tag"] = summary_by_tag


def insert_new_report(database: Database, report):
    """Insert a new report in the reports collection."""
    report.pop("_id", None)
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)
    return dict(ok=True)


def insert_new_reports_overview(database: Database, reports_overview):
    """Insert a new reports overview in the reports overview collection."""
    reports_overview.pop("_id", None)
    reports_overview["timestamp"] = iso_timestamp()
    database.reports_overviews.insert(reports_overview)
    return dict(ok=True)
