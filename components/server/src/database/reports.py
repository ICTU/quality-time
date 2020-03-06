"""Reports collection."""

from collections import namedtuple
from typing import cast, Any, Dict, List, Union

import pymongo
from pymongo.database import Database

from server_utilities.functions import iso_timestamp, unique
from server_utilities.type import Change, MetricId, ReportId, SourceId, SubjectId
from model.queries import get_metric_uuid, get_report_uuid, get_subject_uuid
from .datamodels import latest_datamodel


def latest_reports(database: Database, max_iso_timestamp: str = ""):
    """Return the latest, undeleted, reports in the reports collection."""
    for report_uuid in database.reports.distinct("report_uuid"):
        report = database.reports.find_one(
            filter={"report_uuid": report_uuid, "timestamp": {"$lt": max_iso_timestamp or iso_timestamp()}},
            sort=[("timestamp", pymongo.DESCENDING)])
        if report and "deleted" not in report:
            report["_id"] = str(report["_id"])
            yield report


def latest_reports_overview(database: Database, max_iso_timestamp: str = "") -> Dict:
    """Return the latest reports overview."""
    timestamp_filter = dict(timestamp={"$lt": max_iso_timestamp or iso_timestamp()})
    if overview := database.reports_overviews.find_one(timestamp_filter, sort=[("timestamp", pymongo.DESCENDING)]):
        overview["_id"] = str(overview["_id"])
    return overview or dict()


def latest_report(database: Database, report_uuid: ReportId):
    """Return the latest report for the specified report uuid."""
    return database.reports.find_one(filter={"report_uuid": report_uuid}, sort=[("timestamp", pymongo.DESCENDING)])


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
    _prepare_reports_for_insertion(*reports)
    if len(reports) > 1:
        database.reports.insert_many(reports, ordered=False)
    else:
        database.reports.insert(reports[0])
    return dict(ok=True)


def insert_new_reports_overview(database: Database, reports_overview) -> Dict[str, Any]:
    """Insert a new reports overview in the reports overview collection."""
    _prepare_reports_for_insertion(reports_overview)
    database.reports_overviews.insert(reports_overview)
    return dict(ok=True)


def _prepare_reports_for_insertion(*reports) -> None:
    """Prepare the report(s) for insertion in the reports collection by removing any ids and setting the timestamp."""
    now = iso_timestamp()
    for report in reports:
        if "_id" in report:
            del report["_id"]
        report["timestamp"] = now


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog, narrowed to a single report, subject, metric, or source if so required.
    The uuids keyword arguments may contain report_uuid="report_uuid", and one of subject_uuid="subject_uuid",
    metric_uuid="metric_uuid", and source_uuid="source_uuid"."""
    sort_order = [("timestamp", pymongo.DESCENDING)]
    projection = {"delta.description": True, "delta.email": True, "timestamp": True}
    delta_filter: Dict[str, Union[Dict, List]] = {"delta": {"$exists": True}}
    changes: List[Change] = []
    if not uuids:
        changes.extend(database.reports_overviews.find(
            filter=delta_filter, sort=sort_order, limit=nr_changes*2, projection=projection))
    old_report_delta_filter = {f"delta.{key}": value for key, value in uuids.items() if value}
    new_report_delta_filter = {"delta.uuids": {"$in": list(uuids.values())}}
    delta_filter["$or"] = [old_report_delta_filter, new_report_delta_filter]
    changes.extend(database.reports.find(
        filter=delta_filter, sort=sort_order, limit=nr_changes*2, projection=projection))
    changes = sorted(changes, reverse=True, key=lambda change: change["timestamp"])
    # Weed out potential duplicates, because when a user moves items between reports both reports get the same delta
    return list(unique(changes, lambda change: cast(Dict[str, str], change["delta"])["description"]))[:nr_changes]


def get_data(database: Database, report_uuid: ReportId = None, subject_uuid: SubjectId = None,
             metric_uuid: MetricId = None, source_uuid: SourceId = None):
    """Return applicable report, subject, metric, source, and their uuids and names."""
    data = namedtuple(
        "data",
        "datamodel, reports, report, report_uuid, report_name, subject, subject_uuid, subject_name, "
        "metric, metric_uuid, metric_name, source, source_uuid, source_name")
    data.datamodel = latest_datamodel(database)
    data.reports = list(latest_reports(database, data.datamodel))
    data.source_uuid = source_uuid
    data.metric_uuid = get_metric_uuid(data.reports, data.source_uuid) if data.source_uuid else metric_uuid
    data.subject_uuid = get_subject_uuid(data.reports, data.metric_uuid) if data.metric_uuid else subject_uuid
    data.report_uuid = get_report_uuid(data.reports, data.subject_uuid) if data.subject_uuid else report_uuid
    data.report = list(filter(lambda report: data.report_uuid == report["report_uuid"], data.reports))[0]
    data.report_name = data.report.get("title") or ""
    if data.subject_uuid:
        data.subject = data.report["subjects"][data.subject_uuid]
        data.subject_name = data.subject.get("name") or data.datamodel["subjects"][data.subject["type"]]["name"]
    if data.metric_uuid:
        data.metric = data.subject["metrics"][data.metric_uuid]
        data.metric_name = data.metric.get("name") or data.datamodel["metrics"][data.metric["type"]]["name"]
    if data.source_uuid:
        data.source = data.metric["sources"][data.source_uuid]
        data.source_name = data.source.get("name") or data.datamodel["sources"][data.source["type"]]["name"]
    return data
