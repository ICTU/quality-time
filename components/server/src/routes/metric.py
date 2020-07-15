"""Metric routes."""

from typing import Any, Dict

import bottle
from pymongo.database import Database

from database import sessions
from database.datamodels import default_metric_attributes
from database.measurements import insert_new_measurement, latest_measurement
from database.reports import insert_new_report, latest_reports, MetricData, SubjectData
from model.actions import copy_metric, move_item
from server_utilities.functions import uuid, sanitize_html
from server_utilities.type import MetricId, SubjectId


@bottle.get("/api/v3/metrics")
def get_metrics(database: Database):
    """Get all metrics."""
    metrics: Dict[str, Any] = {}
    for report in latest_reports(database):
        for subject in report["subjects"].values():
            for metric_uuid, metric in subject["metrics"].items():
                metric["report_uuid"] = report["report_uuid"]
                metrics[metric_uuid] = metric
    return metrics


@bottle.post("/api/v3/metric/new/<subject_uuid>")
def post_metric_new(subject_uuid: SubjectId, database: Database):
    """Add a new metric."""
    data = SubjectData(database, subject_uuid)
    data.subject["metrics"][(metric_uuid := uuid())] = default_metric_attributes(database)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, metric_uuid], email=user["email"],
        description=f"{user['user']} added a new metric to subject '{data.subject_name}' in report "
                    f"'{data.report_name}'.")
    result = insert_new_report(database, data.report)
    result["new_metric_uuid"] = metric_uuid
    return result


@bottle.post("/api/v3/metric/<metric_uuid>/copy/<subject_uuid>")
def post_metric_copy(metric_uuid: MetricId, subject_uuid: SubjectId, database: Database):
    """Add a copy of the metric to the subject (new in v3)."""
    source = MetricData(database, metric_uuid)
    target = SubjectData(database, subject_uuid)
    target.subject["metrics"][(metric_copy_uuid := uuid())] = copy_metric(source.metric, source.datamodel)
    user = sessions.user(database)
    target.report["delta"] = dict(
        uuids=[target.report_uuid, target.subject_uuid, metric_copy_uuid], email=user["email"],
        description=f"{user['user']} copied the metric '{source.metric_name}' of subject "
                    f"'{source.subject_name}' from report '{source.report_name}' to subject '{target.subject_name}' "
                    f"in report '{target.report_name}'.")
    result = insert_new_report(database, target.report)
    result["new_metric_uuid"] = metric_copy_uuid
    return result


@bottle.post("/api/v3/metric/<metric_uuid>/move/<target_subject_uuid>")
def post_move_metric(metric_uuid: MetricId, target_subject_uuid: SubjectId, database: Database):
    """Move the metric to another subject."""
    source = MetricData(database, metric_uuid)
    target = SubjectData(database, target_subject_uuid)
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
        target_uuids = [target.report_uuid, target_subject_uuid, metric_uuid]
    target.report["delta"] = dict(uuids=target_uuids, email=user["email"], description=delta_description)
    return insert_new_report(database, source.report, target.report)


@bottle.delete("/api/v3/metric/<metric_uuid>")
def delete_metric(metric_uuid: MetricId, database: Database):
    """Delete a metric."""
    data = MetricData(database, metric_uuid)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, metric_uuid], email=user["email"],
        description=f"{user['user']} deleted metric '{data.metric_name}' from subject "
                    f"'{data.subject_name}' in report '{data.report_name}'.")
    del data.subject["metrics"][metric_uuid]
    return insert_new_report(database, data.report)


@bottle.post("/api/v3/metric/<metric_uuid>/attribute/<metric_attribute>")
def post_metric_attribute(metric_uuid: MetricId, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    value = dict(bottle.request.json)[metric_attribute]
    data = MetricData(database, metric_uuid)
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
    attributes_impacting_status = ("accept_debt", "debt_target", "debt_end_date", "direction", "near_target", "target")
    if metric_attribute in attributes_impacting_status and (latest := latest_measurement(database, metric_uuid)):
        return insert_new_measurement(database, data.metric, latest)
    return dict(ok=True)
