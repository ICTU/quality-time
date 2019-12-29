"""Metric routes."""

from typing import Any, Dict

import bottle
from pymongo.database import Database

from database import sessions
from database.datamodels import default_metric_attributes
from database.reports import copy_metric, get_data, insert_new_report, move_item
from server_utilities.functions import uuid, sanitize_html
from server_utilities.type import MetricId, ReportId, SubjectId
from .measurement import latest_measurement, insert_new_measurement
from .reports import get_reports


@bottle.get("/api/v1/metrics")
def get_metrics(database: Database):
    """Get all metrics."""
    metrics: Dict[str, Any] = {}
    reports = get_reports(database)
    for report in reports["reports"]:
        for subject in report["subjects"].values():
            metrics.update(subject["metrics"])
    return metrics


@bottle.post("/api/v1/report/<report_uuid>/subject/<subject_uuid>/metric/new")
def post_metric_new(report_uuid: ReportId, subject_uuid: SubjectId, database: Database):
    """Add a new metric."""
    data = get_data(database, report_uuid, subject_uuid)
    data.subject["metrics"][uuid()] = default_metric_attributes(database, report_uuid)
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid,
        description=f"{sessions.user(database)} added a new metric to subject '{data.subject_name}' in report "
                    f"'{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/metric/<metric_uuid>/copy")
def post_metric_copy(report_uuid: ReportId, metric_uuid: MetricId, database: Database):
    """Copy a metric."""
    data = get_data(database, report_uuid, metric_uuid=metric_uuid)
    data.subject["metrics"][uuid()] = copy_metric(data.metric)
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid, metric_uuid=data.metric_uuid,
        description=f"{sessions.user(database)} copied the metric '{data.metric_name}' of subject "
                    f"'{data.subject_name}' in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.delete("/api/v1/report/<report_uuid>/metric/<metric_uuid>")
def delete_metric(report_uuid: ReportId, metric_uuid: MetricId, database: Database):
    """Delete a metric."""
    data = get_data(database, report_uuid, metric_uuid=metric_uuid)
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid,
        description=f"{sessions.user(database)} deleted metric '{data.metric_name}' from subject '{data.subject_name}' "
                    f"in report '{data.report_name}'.")
    del data.subject["metrics"][metric_uuid]
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/metric/<metric_uuid>/<metric_attribute>")
def post_metric_attribute(report_uuid: ReportId, metric_uuid: MetricId, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    value = dict(bottle.request.json)[metric_attribute]
    data = get_data(database, report_uuid, metric_uuid=metric_uuid)
    old_value = data.metric.get(metric_attribute) or ""
    if metric_attribute == "comment" and value:
        value = sanitize_html(value)
    if metric_attribute == "position":
        old_value, value = move_item(data, value, "metric")
    else:
        data.metric[metric_attribute] = value
    if old_value == value:
        return dict(ok=True)  # Nothing to do
    if metric_attribute == "type":
        data.metric.update(default_metric_attributes(database, report_uuid, value))
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid, metric_uuid=metric_uuid,
        description=f"{sessions.user(database)} changed the {metric_attribute} of metric '{data.metric_name}' of "
                    f"subject '{data.subject_name}' in report '{data.report_name}' from '{old_value}' to '{value}'.")
    insert_new_report(database, data.report)
    if metric_attribute in ("accept_debt", "debt_target", "debt_end_date", "direction", "near_target", "target"):
        if latest := latest_measurement(database, metric_uuid):
            return insert_new_measurement(database, data.metric, latest)
    return dict(ok=True)
