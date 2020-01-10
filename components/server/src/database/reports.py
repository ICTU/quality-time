"""Reports collection."""

from collections import namedtuple
from typing import cast, Any, Dict, List, Optional, Tuple

import pymongo
from pymongo.database import Database

from server_utilities.functions import iso_timestamp
from server_utilities.type import Change, Color, MetricId, ReportId, SourceId, Status, SubjectId
from .datamodels import latest_datamodel
from .measurements import last_measurements


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
    timestamp_filter = dict(timestamp={"$lt": max_iso_timestamp or iso_timestamp()})
    if overview := database.reports_overviews.find_one(timestamp_filter, sort=[("timestamp", pymongo.DESCENDING)]):
        overview["_id"] = str(overview["_id"])
    return overview or dict()


def summarize_report(database: Database, report) -> None:
    """Add a summary of the measurements to each subject."""
    status_color_mapping: Dict[Status, Color] = dict(
        target_met="green", debt_target_met="grey", near_target_met="yellow", target_not_met="red")
    report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=0)
    report["summary_by_subject"] = {}
    report["summary_by_tag"] = {}
    last_measurements_by_metric_uuid = {m["metric_uuid"]: m for m in last_measurements(database)}
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
            for tag in metric.get("tags", []):
                report["summary_by_tag"].setdefault(tag, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1


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
    """Return the changelog, narrowed to a single report, subject, metric, or source if so required.
    The uuids keyword arguments may contain report_uuid="report_uuid", and one of subject_uuid="subject_uuid",
    metric_uuid="metric_uuid", and source_uuid="source_uuid"."""
    sort_order = [("timestamp", pymongo.DESCENDING)]
    projection = {"delta.description": True, "timestamp": True}
    changes: List[Change] = []
    if not uuids:
        changes.extend(database.reports_overviews.find(sort=sort_order, limit=nr_changes, projection=projection))
    old_delta_filter = {f"delta.{key}": value for key, value in uuids.items() if value}
    delta_filter = {"$or": [old_delta_filter, {"delta.uuids": {"$in": list(uuids.values())}}]}
    changes.extend(database.reports.find(filter=delta_filter, sort=sort_order, limit=nr_changes, projection=projection))
    return sorted(changes, reverse=True, key=lambda change: change["timestamp"])[:nr_changes]


def _get_report_uuid(reports, subject_uuid: SubjectId) -> Optional[ReportId]:
    """Return the uuid of the report that contains the subject with the specified uuid."""
    return cast(ReportId, [report for report in reports if subject_uuid in report["subjects"]][0]["report_uuid"])


def _get_subject_uuid(reports, metric_uuid: MetricId) -> Optional[SubjectId]:
    """Return the uuid of the subject that has the metric with the specified uuid."""
    subjects: List[Tuple[SubjectId, Any]] = []
    for report in reports:
        subjects.extend(report["subjects"].items())
    return [subject_uuid for (subject_uuid, subject) in subjects if metric_uuid in subject["metrics"]][0]


def _get_metric_uuid(reports, source_uuid: SourceId) -> Optional[MetricId]:
    """Return the uuid of the metric that has a source with the specified uuid."""
    metrics: List[Tuple[MetricId, Any]] = []
    for report in reports:
        for subject in report["subjects"].values():
            metrics.extend(subject["metrics"].items())
    return [metric_uuid for (metric_uuid, metric) in metrics if source_uuid in metric["sources"]][0]


def get_data(database: Database, report_uuid: ReportId = None, subject_uuid: SubjectId = None,
             metric_uuid: MetricId = None, source_uuid: SourceId = None):
    """Return applicable report, subject, metric, source, and their uuids and names."""
    data = namedtuple(
        "data",
        "datamodel, reports, report, report_uuid, report_name, subject, subject_uuid, subject_name, "
        "metric, metric_uuid, metric_name, source, source_uuid, source_name")
    data.reports = latest_reports(database)
    data.datamodel = latest_datamodel(database)
    data.source_uuid = source_uuid
    data.metric_uuid = _get_metric_uuid(data.reports, data.source_uuid) if data.source_uuid else metric_uuid
    data.subject_uuid = _get_subject_uuid(data.reports, data.metric_uuid) if data.metric_uuid else subject_uuid
    data.report_uuid = _get_report_uuid(data.reports, data.subject_uuid) if data.subject_uuid else report_uuid
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
