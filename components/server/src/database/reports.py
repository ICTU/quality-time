"""Reports collection."""

from collections import namedtuple
from typing import Callable, Dict, List, Literal, Tuple

import pymongo
from pymongo.database import Database

from server_utilities.functions import iso_timestamp, uuid
from server_utilities.type import Change, Color, MetricId, Position, ReportId, SourceId, Status, SubjectId
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


def latest_report(database: Database, report_uuid: ReportId):
    """Return the latest report for the specified report uuid."""
    return database.reports.find_one(filter={"report_uuid": report_uuid}, sort=[("timestamp", pymongo.DESCENDING)])


def latest_metric(database: Database, report_uuid: ReportId, metric_uuid: MetricId):
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
    """Return the changelog, narrowed to a single report, subject, metric, or source if so required.
    The uuids keyword arguments may contain report_uuid="report_uuid", and one of subject_uuid="subject_uuid",
    metric_uuid="metric_uuid", and source_uuid="source_uuid"."""
    sort_order = [("timestamp", pymongo.DESCENDING)]
    projection = {"delta.description": True, "timestamp": True}
    changes: List[Change] = []
    if not uuids:
        changes.extend(database.reports_overviews.find(sort=sort_order, limit=nr_changes, projection=projection))
    delta_filter = {f"delta.{key}": value for key, value in uuids.items() if value}
    changes.extend(database.reports.find(filter=delta_filter, sort=sort_order, limit=nr_changes, projection=projection))
    return sorted(changes, reverse=True, key=lambda change: change["timestamp"])[:nr_changes]


def get_subject_uuid(report, metric_uuid: MetricId):
    """Return the uuid of the subject that has the metric with the specified uuid."""
    subjects = report["subjects"]
    return [subject_uuid for subject_uuid in subjects if metric_uuid in subjects[subject_uuid]["metrics"]][0]


def get_metric_uuid(report, source_uuid: SourceId):
    """Return the uuid of the metric that has a source with the specified uuid."""
    return [metric_uuid for subject in report["subjects"].values() for metric_uuid in subject["metrics"]
            if source_uuid in subject["metrics"][metric_uuid]["sources"]][0]


def get_data(database: Database, report_uuid: ReportId, subject_uuid: SubjectId = None, metric_uuid: MetricId = None,
             source_uuid: SourceId = None):
    """Return applicable report, subject, metric, source, and their uuids and names."""
    data = namedtuple(
        "data",
        "datamodel, report, report_name, subject, subject_uuid, subject_name, "
        "metric, metric_uuid, metric_name, source, source_uuid, source_name")
    data.report = latest_report(database, report_uuid)
    data.report_name = data.report.get("title") or ""
    data.source_uuid = source_uuid
    data.metric_uuid = get_metric_uuid(data.report, data.source_uuid) if data.source_uuid else metric_uuid
    data.subject_uuid = get_subject_uuid(data.report, data.metric_uuid) if data.metric_uuid else subject_uuid
    data.datamodel = latest_datamodel(database)
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


def _copy_item(item, sub_items: str, copy_sub_item: Callable):
    """Return a copy of the item and its sub-items."""
    item_copy = item.copy()
    item_copy[sub_items] = dict((uuid(), copy_sub_item(sub_item)) for sub_item in item[sub_items].values())
    return item_copy


def copy_metric(metric):
    """Return a copy of the metric and its sources."""
    return _copy_item(metric, "sources", dict.copy)


def copy_subject(subject):
    """Return a copy of the subject, its metrics, and their sources."""
    return _copy_item(subject, "metrics", copy_metric)


def copy_report(report):
    """Return a copy of the report, its subjects, their metrics, and their sources."""
    return _copy_item(report, "subjects", copy_subject)


def move_item(data, new_position: Position, item_type: Literal["metric", "subject"]) -> Tuple[int, int]:
    """Change the item position."""
    container = data.report if item_type == "subject" else data.subject
    items = container[item_type + "s"]
    nr_items = len(items)
    item_to_move = getattr(data, item_type)
    item_to_move_id = getattr(data, f"{item_type}_uuid")
    old_index = list(items.keys()).index(item_to_move_id)
    new_index = dict(
        first=0, last=nr_items - 1, previous=max(0, old_index - 1), next=min(nr_items - 1, old_index + 1))[new_position]
    # Dicts are guaranteed to be (insertion) ordered starting in Python 3.7, but there's no API to change the order so
    # we construct a new dict in the right order and insert that in the report.
    reordered_items: Dict[str, Dict] = dict()
    del items[item_to_move_id]
    for item_id, item in items.items():
        if len(reordered_items) == new_index:
            reordered_items[item_to_move_id] = item_to_move
        reordered_items[item_id] = item
    if len(reordered_items) == new_index:
        reordered_items[item_to_move_id] = item_to_move
    container[item_type + "s"] = reordered_items
    return old_index, new_index
