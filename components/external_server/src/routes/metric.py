"""Metric routes."""

from typing import Any

import bottle
from pymongo.database import Database

from shared.database.datamodels import latest_datamodel
from shared.database.measurements import insert_new_measurement, latest_measurement
from shared.database.reports import insert_new_report
from shared.model.metric import Metric
from shared.utils.type import MetricId, SubjectId

from database.datamodels import default_metric_attributes
from database.reports import latest_report_for_uuids, latest_reports
from model.actions import copy_metric, move_item
from utils.functions import sanitize_html, uuid

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION


@bottle.post("/api/v3/metric/new/<subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_new(subject_uuid: SubjectId, database: Database):
    """Add a new metric."""
    data_model = latest_datamodel(database)
    all_reports = latest_reports(database, data_model)
    report = latest_report_for_uuids(all_reports, subject_uuid)[0]
    subject = report.subjects_dict[subject_uuid]
    metric_type = str(dict(bottle.request.json)["type"])
    subject.metrics_dict[(metric_uuid := uuid())] = default_metric_attributes(database, metric_type)
    description = f"{{user}} added a new metric to subject '{subject.name}' in report '{report.name}'."
    uuids = [report.uuid, subject.uuid, metric_uuid]
    result = insert_new_report(database, description, uuids, report)
    result["new_metric_uuid"] = metric_uuid
    return result


@bottle.post("/api/v3/metric/<metric_uuid>/copy/<subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_copy(metric_uuid: MetricId, subject_uuid: SubjectId, database: Database):
    """Add a copy of the metric to the subject (new in v3)."""
    data_model = latest_datamodel(database)
    all_reports = latest_reports(database, data_model)
    source_and_target_reports = latest_report_for_uuids(all_reports, metric_uuid, subject_uuid)
    source_report = source_and_target_reports[0]
    target_report = source_and_target_reports[1]
    source_metric, source_subject = source_report.instance_and_parents_for_uuid(metric_uuid=metric_uuid)
    target_subject = target_report.subjects_dict[subject_uuid]
    target_subject.metrics_dict[(metric_copy_uuid := uuid())] = copy_metric(source_metric, data_model)
    description = (
        f"{{user}} copied the metric '{source_metric.name}' of subject '{source_subject.name}' from report "
        f"'{source_report.name}' to subject '{target_subject.name}' in report '{target_report.name}'."
    )
    uuids = [target_report.uuid, target_subject.uuid, metric_copy_uuid]
    result = insert_new_report(database, description, uuids, target_report)
    result["new_metric_uuid"] = metric_copy_uuid
    return result


@bottle.post("/api/v3/metric/<metric_uuid>/move/<target_subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_move_metric(metric_uuid: MetricId, target_subject_uuid: SubjectId, database: Database):
    """Move the metric to another subject."""
    data_model = latest_datamodel(database)
    all_reports = latest_reports(database, data_model)
    source_and_target_reports = latest_report_for_uuids(all_reports, metric_uuid, target_subject_uuid)
    source_report = source_and_target_reports[0]
    target_report = source_and_target_reports[1]
    metric, source_subject = source_report.instance_and_parents_for_uuid(metric_uuid=metric_uuid)
    target_subject = target_report.subjects_dict[target_subject_uuid]
    delta_description = (
        f"{{user}} moved the metric '{metric.name}' from subject '{source_subject.name}' in report "
        f"'{source_report.name}' to subject '{target_subject.name}' in report '{target_report.name}'."
    )
    target_subject.metrics_dict[metric_uuid] = metric
    uuids = [target_report.uuid, source_report.uuid, source_subject.uuid, target_subject.uuid, metric.uuid]
    if target_report.uuid == source_report.uuid:
        # Metric is moved within the same report
        del source_subject.metrics_dict[metric_uuid]
        reports_to_insert = [target_report]
    else:
        # Metric is moved from one report to another, update both
        del source_subject.metrics_dict[metric_uuid]
        reports_to_insert = [target_report, source_report]
    return insert_new_report(database, delta_description, uuids, *reports_to_insert)


@bottle.delete("/api/v3/metric/<metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def delete_metric(metric_uuid: MetricId, database: Database):
    """Delete a metric."""
    data_model = latest_datamodel(database)
    all_reports = latest_reports(database, data_model)
    report = latest_report_for_uuids(all_reports, metric_uuid)[0]
    metric, subject = report.instance_and_parents_for_uuid(metric_uuid=metric_uuid)
    description = f"{{user}} deleted metric '{metric.name}' from subject '{subject.name}' in report '{report.name}'."
    uuids = [report.uuid, subject.uuid, metric_uuid]
    del subject.metrics_dict[metric_uuid]
    return insert_new_report(database, description, uuids, report)


ATTRIBUTES_IMPACTING_STATUS = (
    "accept_debt",
    "debt_target",
    "debt_end_date",
    "direction",
    "evaluate_targets",
    "issue_ids",
    "near_target",
    "target",
)


@bottle.post("/api/v3/metric/<metric_uuid>/attribute/<metric_attribute>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_attribute(metric_uuid: MetricId, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    new_value = dict(bottle.request.json)[metric_attribute]
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    report = latest_report_for_uuids(reports, metric_uuid)[0]
    metric, subject = report.instance_and_parents_for_uuid(metric_uuid=metric_uuid)
    old_metric_name = metric.name  # in case the name is the attribute that will be changed
    if metric_attribute == "comment" and new_value:
        new_value = sanitize_html(new_value)
    old_value: Any
    if metric_attribute == "position":
        old_value, new_value = move_item(subject, metric, new_value)
    else:
        old_value = metric.get(metric_attribute) or ""
    if old_value == new_value:
        return dict(ok=True)  # Nothing to do
    metric[metric_attribute] = new_value
    if metric_attribute == "type":
        metric.update(default_metric_attributes(database, new_value))
    description = (
        f"{{user}} changed the {metric_attribute} of metric '{old_metric_name}' of subject "
        f"'{subject.name}' in report '{report.name}' from '{old_value}' to '{new_value}'."
    )
    uuids = [report.uuid, subject.uuid, metric.uuid]
    insert_new_report(database, description, uuids, report)
    metric = Metric(data_model, metric, metric_uuid)
    if metric_attribute in ATTRIBUTES_IMPACTING_STATUS and (latest := latest_measurement(database, metric)):
        return insert_new_measurement(database, latest.copy())
    return dict(ok=True)


@bottle.post("/api/v3/metric/<metric_uuid>/issue/new", permissions_required=[EDIT_REPORT_PERMISSION])
def add_metric_issue(metric_uuid: MetricId, database: Database):
    """Add a new issue to the metric using the configured issue tracker."""
    reports = latest_reports(database, latest_datamodel(database))
    report = latest_report_for_uuids(reports, metric_uuid)[0]
    metric, subject = report.instance_and_parents_for_uuid(metric_uuid=metric_uuid)
    issue_tracker = report.issue_tracker()
    issue_summary = f"Quality-time metric '{metric.name}'"
    issue_description = create_issue_description(metric, subject, report)
    issue_key, error = issue_tracker.create_issue(issue_summary, issue_description)
    if error:  # pylint: disable=no-else-return
        return dict(ok=False, error=error)
    else:  # pragma: no cover
        old_issue_ids = metric.get("issue_ids") or []
        new_issue_ids = sorted([issue_key, *old_issue_ids])
        description = (
            f"{{user}} changed the issue_ids of metric '{metric.name}' of subject "
            f"'{subject.name}' in report '{report.name}' from '{old_issue_ids}' to '{new_issue_ids}'."
        )
        report["subjects"][subject.uuid]["metrics"][metric_uuid]["issue_ids"] = new_issue_ids
        insert_new_report(database, description, [report.uuid, subject.uuid, metric.uuid], report)
        return dict(ok=True, issue_url=issue_tracker.browse_url(issue_key))


def create_issue_description(metric, subject, report) -> str:
    """Create an issue description for the metric."""
    metric_url = dict(bottle.request.json)["metric_url"]
    return (
        f"Metric '[{metric.name}|{metric_url}]' of subject '{subject.name}' "
        f"in Quality-time report '{report.name}' needs attention."
    )
