"""Reports collection."""

from typing import Any, Dict, List, Union, cast

import pymongo
from pymongo.database import Database

from server_utilities.functions import iso_timestamp, unique
from server_utilities.type import Change, MetricId, ReportId

# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]
# Filters:
DOES_EXIST = {"$exists": True}
DOES_NOT_EXIST = {"$exists": False}


def latest_reports(database: Database, max_iso_timestamp: str = ""):
    """Return the latest, undeleted, reports in the reports collection."""
    reports = list(database.reports.find(
        {"last": True, "deleted": DOES_NOT_EXIST, "timestamp": {"$lt": max_iso_timestamp or iso_timestamp()}}))
    for report in reports:
        report["_id"] = str(report["_id"])
    return reports


def latest_reports_overview(database: Database, max_iso_timestamp: str = "") -> Dict:
    """Return the latest reports overview."""
    timestamp_filter = dict(timestamp={"$lt": max_iso_timestamp or iso_timestamp()})
    overview = database.reports_overviews.find_one(timestamp_filter, sort=TIMESTAMP_DESCENDING)
    if overview:  # pragma: no cover-behave
        overview["_id"] = str(overview["_id"])
    return overview or {}


def report_exists(database: Database, report_uuid: ReportId):
    """Return whether a report with the specified report uuid exists."""
    return report_uuid in database.reports.distinct("report_uuid")


def latest_metric(database: Database, metric_uuid: MetricId):
    """Return the latest metric with the specified metric uuid."""
    for report in latest_reports(database):
        for subject in report.get("subjects", {}).values():
            metrics = subject.get("metrics", {})
            if metric_uuid in metrics:
                return metrics[metric_uuid]
    return None


def insert_new_report(database: Database, *reports) -> Dict[str, Any]:
    """Insert one or more new reports in the reports collection."""
    _prepare_documents_for_insertion(*reports, last=True)
    report_uuids = [report["report_uuid"] for report in reports]
    database.reports.update_many({"report_uuid": {"$in": report_uuids}, "last": DOES_EXIST}, {"$unset": {"last": ""}})
    if len(reports) > 1:
        database.reports.insert_many(reports, ordered=False)
    else:
        database.reports.insert(reports[0])
    return dict(ok=True)


def insert_new_reports_overview(database: Database, reports_overview) -> Dict[str, Any]:
    """Insert a new reports overview in the reports overview collection."""
    _prepare_documents_for_insertion(reports_overview)
    database.reports_overviews.insert(reports_overview)
    return dict(ok=True)


def _prepare_documents_for_insertion(*documents, **extra_attributes) -> None:
    """Prepare the documents for insertion in the database by removing any ids and setting the extra attributes."""
    now = iso_timestamp()
    for document in documents:
        if "_id" in document:
            del document["_id"]
        document["timestamp"] = now
        for key, value in extra_attributes.items():
            document[key] = value


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog, narrowed to a single report, subject, metric, or source if so required.
    The uuids keyword arguments may contain report_uuid="report_uuid", and one of subject_uuid="subject_uuid",
    metric_uuid="metric_uuid", and source_uuid="source_uuid"."""
    projection = {"delta.description": True, "delta.email": True, "timestamp": True}
    delta_filter: Dict[str, Union[Dict, List]] = {"delta": DOES_EXIST}
    changes: List[Change] = []
    if not uuids:
        changes.extend(database.reports_overviews.find(
            filter=delta_filter, sort=TIMESTAMP_DESCENDING, limit=nr_changes*2, projection=projection))
    old_report_delta_filter = {f"delta.{key}": value for key, value in uuids.items() if value}
    new_report_delta_filter = {"delta.uuids": {"$in": list(uuids.values())}}
    delta_filter["$or"] = [old_report_delta_filter, new_report_delta_filter]
    changes.extend(database.reports.find(
        filter=delta_filter, sort=TIMESTAMP_DESCENDING, limit=nr_changes*2, projection=projection))
    changes = sorted(changes, reverse=True, key=lambda change: change["timestamp"])
    # Weed out potential duplicates, because when a user moves items between reports both reports get the same delta
    return list(unique(changes, lambda change: cast(Dict[str, str], change["delta"])["description"]))[:nr_changes]
