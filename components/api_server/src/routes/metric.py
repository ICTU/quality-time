"""Metric routes."""

from datetime import UTC, datetime, timedelta
from typing import Any, cast

import bottle
from pymongo.database import Database

from shared.database.measurements import insert_new_measurement, latest_measurement, latest_successful_measurement
from shared.model.metric import Metric
from shared.utils.type import MetricId, SubjectId, Value
from shared_data_model import DATA_MODEL

from database.reports import insert_new_report, latest_report_for_uuids, latest_reports
from model.actions import copy_metric, move_item
from model.defaults import default_metric_attributes
from utils.functions import sanitize_html, uuid

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION


@bottle.post("/api/v3/metric/new/<subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_new(subject_uuid: SubjectId, database: Database):
    """Add a new metric."""
    all_reports = latest_reports(database)
    report = latest_report_for_uuids(all_reports, subject_uuid)[0]
    subject = report.subjects_dict[subject_uuid]
    metric_type = str(dict(bottle.request.json)["type"])
    metric_uuid = cast(MetricId, uuid())
    subject.metrics_dict[metric_uuid] = cast(Metric, default_metric_attributes(metric_type))
    description = f"{{user}} added a new metric to subject '{subject.name}' in report '{report.name}'."
    uuids = [report.uuid, subject.uuid, metric_uuid]
    result = insert_new_report(database, description, uuids, report)
    result["new_metric_uuid"] = metric_uuid
    return result


@bottle.post("/api/v3/metric/<metric_uuid>/copy/<subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_copy(metric_uuid: MetricId, subject_uuid: SubjectId, database: Database):
    """Add a copy of the metric to the subject (new in v3)."""
    all_reports = latest_reports(database)
    source_and_target_reports = latest_report_for_uuids(all_reports, metric_uuid, subject_uuid)
    source_report = source_and_target_reports[0]
    target_report = source_and_target_reports[1]
    source_metric, source_subject = source_report.instance_and_parents_for_uuid(metric_uuid=metric_uuid)
    target_subject = target_report.subjects_dict[subject_uuid]
    metric_copy_uuid = cast(MetricId, uuid())
    target_subject.metrics_dict[metric_copy_uuid] = copy_metric(source_metric)
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
    all_reports = latest_reports(database)
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
    all_reports = latest_reports(database)
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
    "type",
)


@bottle.post("/api/v3/metric/<metric_uuid>/attribute/<metric_attribute>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_attribute(metric_uuid: MetricId, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    new_value = dict(bottle.request.json)[metric_attribute]
    reports = latest_reports(database)
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
        return {"ok": True}  # Nothing to do
    if metric_attribute == "type":
        # Update the metric attributes, but keep the sources and the user supplied tags
        default_tags_old_type = DATA_MODEL.metrics[metric.type()].tags or []
        user_supplied_tags = [tag for tag in metric["tags"] if tag not in default_tags_old_type]
        metric.update(default_metric_attributes(new_value), sources=metric["sources"])
        metric["tags"].extend(user_supplied_tags)
    metric[metric_attribute] = new_value
    description = (
        f"{{user}} changed the {metric_attribute} of metric '{old_metric_name}' of subject "
        f"'{subject.name}' in report '{report.name}' from '{old_value}' to '{new_value}'."
    )
    insert_new_report(database, description, [report.uuid, subject.uuid, metric.uuid], report)
    metric = Metric(DATA_MODEL.dict(), metric, metric_uuid)
    if metric_attribute in ATTRIBUTES_IMPACTING_STATUS and (latest := latest_measurement(database, metric)):
        return insert_new_measurement(database, latest.copy())
    return {"ok": True}


@bottle.post("/api/v3/metric/<metric_uuid>/debt", permissions_required=[EDIT_REPORT_PERMISSION])
def post_metric_debt(metric_uuid: MetricId, database: Database):
    """Turn the technical debt on or off, including technical debt target and end date."""
    new_accept_debt = dict(bottle.request.json)["accept_debt"]
    report = latest_report_for_uuids(latest_reports(database), metric_uuid)[0]
    metric, subject = report.instance_and_parents_for_uuid(metric_uuid=metric_uuid)
    if new_accept_debt:
        # Get the latest measurement to get the current metric value:
        latest = latest_measurement(database, Metric(DATA_MODEL.dict(), metric, metric_uuid))
        # Only if the metric has at least one measurement can a technical debt target be set:
        new_debt_target = latest.value() if latest else None
        today = datetime.now(tz=UTC).date()
        new_end_date = (today + timedelta(days=report.desired_response_time("debt_target_met"))).isoformat()
    else:
        new_debt_target = None
        new_end_date = None
    old_accept_debt = metric.get("accept_debt") or False
    old_debt_target = metric.get("debt_target")
    old_end_date = metric.get("debt_end_date")
    if old_accept_debt == new_accept_debt and old_debt_target == new_debt_target and old_end_date == new_end_date:
        return {"ok": True}  # Nothing to do
    metric.update(accept_debt=new_accept_debt, debt_target=new_debt_target, debt_end_date=new_end_date)
    description = "{user} changed"
    attribute_descriptions = []
    if new_accept_debt != old_accept_debt:
        attribute_descriptions.append(f" the accepted debt from '{old_accept_debt}' to '{new_accept_debt}'")
    if new_debt_target != old_debt_target:
        attribute_descriptions.append(f" the debt target from '{old_debt_target}' to '{new_debt_target}'")
    if new_end_date != old_end_date:
        attribute_descriptions.append(f" the debt end date from '{old_end_date}' to '{new_end_date}'")
    description += " and".join(attribute_descriptions)
    description += f" of metric '{metric.name}' of subject '{subject.name}' in report '{report.name}'."
    insert_new_report(database, description, [report.uuid, subject.uuid, metric.uuid], report)
    if latest := latest_measurement(database, Metric(DATA_MODEL.dict(), metric, metric_uuid)):
        return insert_new_measurement(database, latest.copy())
    return {"ok": True}


@bottle.post("/api/v3/metric/<metric_uuid>/issue/new", permissions_required=[EDIT_REPORT_PERMISSION])
def add_metric_issue(metric_uuid: MetricId, database: Database):
    """Add a new issue to the metric using the configured issue tracker."""
    report = latest_report_for_uuids(latest_reports(database), metric_uuid)[0]
    metric, subject = report.instance_and_parents_for_uuid(metric_uuid=metric_uuid)
    last_measurement = latest_successful_measurement(database, metric)
    measured_value = last_measurement.value() if last_measurement else "missing"
    issue_tracker = report.issue_tracker()
    issue_key, error = issue_tracker.create_issue(*create_issue_text(metric, measured_value))
    if error:
        return {"ok": False, "error": error}
    else:  # pragma: no feature-test-cover # noqa: RET505
        old_issue_ids = metric.get("issue_ids") or []
        new_issue_ids = sorted([issue_key, *old_issue_ids])
        description = (
            f"{{user}} changed the issue_ids of metric '{metric.name}' of subject "
            f"'{subject.name}' in report '{report.name}' from '{old_issue_ids}' to '{new_issue_ids}'."
        )
        report["subjects"][subject.uuid]["metrics"][metric_uuid]["issue_ids"] = new_issue_ids
        insert_new_report(database, description, [report.uuid, subject.uuid, metric.uuid], report)
        return {"ok": True, "issue_url": issue_tracker.browse_url(issue_key)}


def create_issue_text(metric: Metric, measured_value: Value) -> tuple[str, str]:
    """Create an issue description for the metric."""
    metric_url = dict(bottle.request.json)["metric_url"]
    source_names = ", ".join([source.name or DATA_MODEL.sources[str(source.type)].name for source in metric.sources])
    source_urls = [url for url in [source.get("parameters", {}).get("url") for source in metric.sources] if url]
    issue_summary = f"Fix {measured_value} {metric.unit} from {source_names}"
    source_url_str = f"\nPlease go to {', '.join(source_urls)} for more details." if source_urls else ""
    issue_description = (
        f"The metric [{metric.name}|{metric_url}] in Quality-time reports "
        f"{measured_value} {metric.unit} from {source_names}.{source_url_str}\n"
    )
    return issue_summary, issue_description
