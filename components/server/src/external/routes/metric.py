"""Metric routes."""

from typing import Any

import bottle
from pymongo.database import Database

from database.datamodels import default_metric_attributes, latest_datamodel
from database.measurements import insert_new_measurement, latest_measurement
from database.reports import insert_new_report, latest_reports
from model.actions import copy_metric, move_item
from model.data import MetricData, SubjectData
from model.metric import Metric
from routes.plugins.auth_plugin import EDIT_REPORT_PERMISSION
from server_utilities.functions import sanitize_html, uuid
from server_utilities.type import MetricId, SubjectId


@bottle.post("/api/v3/metric/new/<subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_new(subject_uuid: SubjectId, database: Database):
    """Add a new metric."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    data = SubjectData(data_model, reports, subject_uuid)
    data.subject["metrics"][(metric_uuid := uuid())] = default_metric_attributes(database)
    description = f"{{user}} added a new metric to subject '{data.subject_name}' in report '{data.report_name}'."
    uuids = [data.report_uuid, data.subject_uuid, metric_uuid]
    result = insert_new_report(database, description, uuids, data.report)
    result["new_metric_uuid"] = metric_uuid
    return result


@bottle.post("/api/v3/metric/<metric_uuid>/copy/<subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_copy(metric_uuid: MetricId, subject_uuid: SubjectId, database: Database):
    """Add a copy of the metric to the subject (new in v3)."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    source = MetricData(data_model, reports, metric_uuid)
    target = SubjectData(data_model, reports, subject_uuid)
    target.subject["metrics"][(metric_copy_uuid := uuid())] = copy_metric(source.metric, source.datamodel)
    description = (
        f"{{user}} copied the metric '{source.metric_name}' of subject '{source.subject_name}' from report "
        f"'{source.report_name}' to subject '{target.subject_name}' in report '{target.report_name}'."
    )
    uuids = [target.report_uuid, target.subject_uuid, metric_copy_uuid]
    result = insert_new_report(database, description, uuids, target.report)
    result["new_metric_uuid"] = metric_copy_uuid
    return result


@bottle.post("/api/v3/metric/<metric_uuid>/move/<target_subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_move_metric(metric_uuid: MetricId, target_subject_uuid: SubjectId, database: Database):
    """Move the metric to another subject."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    source = MetricData(data_model, reports, metric_uuid)
    target = SubjectData(data_model, reports, target_subject_uuid)
    delta_description = (
        f"{{user}} moved the metric '{source.metric_name}' from subject '{source.subject_name}' in report "
        f"'{source.report_name}' to subject '{target.subject_name}' in report '{target.report_name}'."
    )
    target.subject["metrics"][metric_uuid] = source.metric
    uuids = [target.report_uuid, source.report_uuid, source.subject_uuid, target_subject_uuid, metric_uuid]
    if target.report_uuid == source.report_uuid:
        # Metric is moved within the same report
        del target.report["subjects"][source.subject_uuid]["metrics"][metric_uuid]
        reports_to_insert = [target.report]
    else:
        # Metric is moved from one report to another, update both
        del source.subject["metrics"][metric_uuid]
        reports_to_insert = [target.report, source.report]
    return insert_new_report(database, delta_description, uuids, *reports_to_insert)


@bottle.delete("/api/v3/metric/<metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def delete_metric(metric_uuid: MetricId, database: Database):
    """Delete a metric."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    data = MetricData(data_model, reports, metric_uuid)
    description = (
        f"{{user}} deleted metric '{data.metric_name}' from subject '{data.subject_name}' in report "
        f"'{data.report_name}'."
    )
    uuids = [data.report_uuid, data.subject_uuid, metric_uuid]
    del data.subject["metrics"][metric_uuid]
    return insert_new_report(database, description, uuids, data.report)


ATTRIBUTES_IMPACTING_STATUS = ("accept_debt", "debt_target", "debt_end_date", "direction", "near_target", "target")


@bottle.post("/api/v3/metric/<metric_uuid>/attribute/<metric_attribute>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_attribute(metric_uuid: MetricId, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    new_value = dict(bottle.request.json)[metric_attribute]
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    data = MetricData(data_model, reports, metric_uuid)
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
    insert_new_report(database, description, uuids, data.report)
    metric = Metric(data.datamodel, data.metric, metric_uuid)
    if metric_attribute in ATTRIBUTES_IMPACTING_STATUS and (latest := latest_measurement(database, metric)):
        return insert_new_measurement(database, latest.copy())
    return dict(ok=True)
