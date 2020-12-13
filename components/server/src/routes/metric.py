"""Metric routes."""

from typing import Any, Dict

import bottle
from pymongo.database import Database

from database.datamodels import default_metric_attributes, latest_datamodel
from database.measurements import insert_new_measurement, latest_measurement
from database.reports import insert_new_report, latest_reports
from model.actions import copy_metric, move_item
from model.data import MetricData, SubjectData
from server_utilities.functions import sanitize_html, uuid
from server_utilities.type import MetricId, SubjectId


@bottle.get("/internal-api/v3/metrics")
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
    data = SubjectData(latest_datamodel(database), latest_reports(database), subject_uuid)
    data.subject["metrics"][(metric_uuid := uuid())] = default_metric_attributes(database)
    description = f"{{user}} added a new metric to subject '{data.subject_name}' in report '{data.report_name}'."
    uuids = [data.report_uuid, data.subject_uuid, metric_uuid]
    data.report["delta"] = dict(uuids=uuids, description=description)
    result = insert_new_report(database, data.report)
    result["new_metric_uuid"] = metric_uuid
    return result


@bottle.post("/api/v3/metric/<metric_uuid>/copy/<subject_uuid>")
def post_metric_copy(metric_uuid: MetricId, subject_uuid: SubjectId, database: Database):
    """Add a copy of the metric to the subject (new in v3)."""
    data_model, reports = latest_datamodel(database), latest_reports(database)
    source = MetricData(data_model, reports, metric_uuid)
    target = SubjectData(data_model, reports, subject_uuid)
    target.subject["metrics"][(metric_copy_uuid := uuid())] = copy_metric(source.metric, source.datamodel)
    description = (
        f"{{user}} copied the metric '{source.metric_name}' of subject '{source.subject_name}' from report "
        f"'{source.report_name}' to subject '{target.subject_name}' in report '{target.report_name}'."
    )
    uuids = [target.report_uuid, target.subject_uuid, metric_copy_uuid]
    target.report["delta"] = dict(uuids=uuids, description=description)
    result = insert_new_report(database, target.report)
    result["new_metric_uuid"] = metric_copy_uuid
    return result


@bottle.post("/api/v3/metric/<metric_uuid>/move/<target_subject_uuid>")
def post_move_metric(metric_uuid: MetricId, target_subject_uuid: SubjectId, database: Database):
    """Move the metric to another subject."""
    data_model, reports = latest_datamodel(database), latest_reports(database)
    source = MetricData(data_model, reports, metric_uuid)
    target = SubjectData(data_model, reports, target_subject_uuid)
    delta_description = (
        f"{{user}} moved the metric '{source.metric_name}' from subject '{source.subject_name}' in report "
        f"'{source.report_name}' to subject '{target.subject_name}' in report '{target.report_name}'."
    )
    target.subject["metrics"][metric_uuid] = source.metric
    reports_to_insert = [target.report]
    if target.report_uuid == source.report_uuid:
        # Metric is moved within the same report
        del target.report["subjects"][source.subject_uuid]["metrics"][metric_uuid]
        target_uuids = [target.report_uuid, source.subject_uuid, target_subject_uuid, metric_uuid]
    else:
        # Metric is moved from one report to another, update both
        reports_to_insert.append(source.report)
        del source.subject["metrics"][metric_uuid]
        source_uuids = [source.report_uuid, source.subject_uuid, metric_uuid]
        source.report["delta"] = dict(uuids=source_uuids, description=delta_description)
        target_uuids = [target.report_uuid, target_subject_uuid, metric_uuid]
    target.report["delta"] = dict(uuids=target_uuids, description=delta_description)
    return insert_new_report(database, *reports_to_insert)


@bottle.delete("/api/v3/metric/<metric_uuid>")
def delete_metric(metric_uuid: MetricId, database: Database):
    """Delete a metric."""
    data = MetricData(latest_datamodel(database), latest_reports(database), metric_uuid)
    description = (
        f"{{user}} deleted metric '{data.metric_name}' from subject '{data.subject_name}' in report "
        f"'{data.report_name}'."
    )
    uuids = [data.report_uuid, data.subject_uuid, metric_uuid]
    data.report["delta"] = dict(uuids=uuids, description=description)
    del data.subject["metrics"][metric_uuid]
    return insert_new_report(database, data.report)


ATTRIBUTES_IMPACTING_STATUS = ("accept_debt", "debt_target", "debt_end_date", "direction", "near_target", "target")


@bottle.post("/api/v3/metric/<metric_uuid>/attribute/<metric_attribute>")
def post_metric_attribute(metric_uuid: MetricId, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    new_value = dict(bottle.request.json)[metric_attribute]
    data = MetricData(latest_datamodel(database), latest_reports(database), metric_uuid)
    if metric_attribute == "comment" and new_value:
        new_value = sanitize_html(new_value)
    old_value: Any
    if metric_attribute == "position":
        old_value, new_value = move_item(data, new_value, "metric")
    else:
        old_value = data.metric.get(metric_attribute) or ""
    if old_value == new_value:
        return dict(ok=True)  # Nothing to do
    data.metric[metric_attribute] = new_value
    if metric_attribute == "type":
        data.metric.update(default_metric_attributes(database, new_value))
    description = (
        f"{{user}} changed the {metric_attribute} of metric '{data.metric_name}' of subject "
        f"'{data.subject_name}' in report '{data.report_name}' from '{old_value}' to '{new_value}'."
    )
    uuids = [data.report_uuid, data.subject_uuid, metric_uuid]
    data.report["delta"] = dict(uuids=uuids, description=description)
    insert_new_report(database, data.report)
    if metric_attribute in ATTRIBUTES_IMPACTING_STATUS and (latest := latest_measurement(database, metric_uuid)):
        return insert_new_measurement(database, data.datamodel, data.metric, latest.copy(), latest)
    return dict(ok=True)
