"""Metric routes."""

from typing import Any, Dict

import bottle
from pymongo.database import Database

from database import sessions
from database.datamodels import default_metric_attributes
from database.reports import get_data, insert_new_report, latest_reports
from model.actions import copy_metric, move_item
from server_utilities.functions import uuid, sanitize_html
from server_utilities.type import MetricId, ReportId, SubjectId
from .measurement import latest_measurement, insert_new_measurement


@bottle.get("/api/v1/metrics")
@bottle.get("/api/v2/metrics")
def get_metrics(database: Database):
    """Get all metrics."""
    metrics: Dict[str, Any] = {}
    for report in latest_reports(database):
        for subject in report["subjects"].values():
            for metric_uuid, metric in subject["metrics"].items():
                metric["report_uuid"] = report["report_uuid"]
                metrics[metric_uuid] = metric
    return metrics


@bottle.post("/api/v1/report/<report_uuid>/subject/<subject_uuid>/metric/new")
def post_metric_new_v1(report_uuid: ReportId, subject_uuid: SubjectId, database: Database):
    """Add a new metric."""
    # pylint: disable=unused-argument
    return post_metric_new(subject_uuid, database)  # pragma: nocover


@bottle.post("/api/v2/metric/new/<subject_uuid>")
def post_metric_new(subject_uuid: SubjectId, database: Database):
    """Add a new metric."""
    data = get_data(database, subject_uuid=subject_uuid)
    data.subject["metrics"][(metric_uuid := uuid())] = default_metric_attributes(database)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, metric_uuid], email=user["email"],
        description=f"{user['user']} added a new metric to subject '{data.subject_name}' in report "
                    f"'{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/metric/<metric_uuid>/copy")
def post_metric_copy_v1(report_uuid: ReportId, metric_uuid: MetricId, database: Database):
    """Copy a metric."""
    # pylint: disable=unused-argument
    return post_metric_copy(metric_uuid, database)  # pragma: nocover


@bottle.post("/api/v2/metric/<metric_uuid>/copy")
def post_metric_copy(metric_uuid: MetricId, database: Database):
    """Copy a metric."""
    data = get_data(database, metric_uuid=metric_uuid)
    data.subject["metrics"][uuid()] = copy_metric(data.metric, data.datamodel)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, data.metric_uuid], email=user["email"],
        description=f"{user['user']} copied the metric '{data.metric_name}' of subject "
                    f"'{data.subject_name}' in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v2/metric/<metric_uuid>/move/<target_subject_uuid>")
def post_move_metric(metric_uuid: MetricId, target_subject_uuid: SubjectId, database: Database):
    """Move the metric to another subject."""
    source = get_data(database, metric_uuid=metric_uuid)
    target = get_data(database, subject_uuid=target_subject_uuid)
    user = sessions.user(database)
    delta_description = f"{user['user']} moved the metric '{source.metric_name}' from subject " \
                        f"'{source.subject_name}' in report '{source.report_name}' to subject " \
                        f"'{target.subject_name}' in report '{target.report_name}'."
    target.subject["metrics"][metric_uuid] = source.metric
    if target.report_uuid == source.report_uuid:
        del target.report["subjects"][source.subject_uuid]["metrics"][metric_uuid]
        target_uuids = [target.report_uuid, source.subject_uuid, target_subject_uuid, metric_uuid]
    else:
        del source.subject["metrics"][metric_uuid]
        source.report["delta"] = dict(
            uuids=[source.report_uuid, source.subject_uuid, metric_uuid], email=user["email"],
            description=delta_description)
        insert_new_report(database, source.report)
        target_uuids = [target.report_uuid, target_subject_uuid, metric_uuid]
    target.report["delta"] = dict(uuids=target_uuids, email=user["email"], description=delta_description)
    return insert_new_report(database, target.report)


@bottle.delete("/api/v1/report/<report_uuid>/metric/<metric_uuid>")
def delete_metric_v1(report_uuid: ReportId, metric_uuid: MetricId, database: Database):
    """Delete a metric."""
    # pylint: disable=unused-argument
    return delete_metric(metric_uuid, database)  # pragma: nocover


@bottle.delete("/api/v2/metric/<metric_uuid>")
def delete_metric(metric_uuid: MetricId, database: Database):
    """Delete a metric."""
    data = get_data(database, metric_uuid=metric_uuid)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, metric_uuid], email=user["email"],
        description=f"{user['user']} deleted metric '{data.metric_name}' from subject "
                    f"'{data.subject_name}' in report '{data.report_name}'.")
    del data.subject["metrics"][metric_uuid]
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/metric/<metric_uuid>/<metric_attribute>")
def post_metric_attribute_v1(report_uuid: ReportId, metric_uuid: MetricId, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    # pylint: disable=unused-argument
    return post_metric_attribute(metric_uuid, metric_attribute, database)  # pragma: nocover


@bottle.post("/api/v2/metric/<metric_uuid>/attribute/<metric_attribute>")
def post_metric_attribute(metric_uuid: MetricId, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    value = dict(bottle.request.json)[metric_attribute]
    data = get_data(database, metric_uuid=metric_uuid)
    if metric_attribute == "comment" and value:
        value = sanitize_html(value)
    old_value: Any
    if metric_attribute == "position":
        old_value, value = move_item(data, value, "metric")
    else:
        old_value = data.metric.get(metric_attribute) or ""
    if old_value == value:
        return dict(ok=True)  # Nothing to do
    data.metric[metric_attribute] = value
    if metric_attribute == "type":
        data.metric.update(default_metric_attributes(database, value))
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, metric_uuid], email=user["email"],
        description=f"{user['user']} changed the {metric_attribute} of metric '{data.metric_name}' "
                    f"of subject '{data.subject_name}' in report '{data.report_name}' from '{old_value}' to '{value}'.")
    insert_new_report(database, data.report)
    if metric_attribute in ("accept_debt", "debt_target", "debt_end_date", "direction", "near_target", "target"):
        if latest := latest_measurement(database, metric_uuid):
            return insert_new_measurement(database, data.metric, latest)
    return dict(ok=True)
