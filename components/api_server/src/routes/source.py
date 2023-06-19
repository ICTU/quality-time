"""Source routes."""

from typing import Any, cast

import bottle
from pymongo.database import Database

from shared.utils.type import ItemId, MetricId, SourceId

from database.datamodels import default_source_parameters, latest_datamodel
from database.reports import insert_new_report, latest_report_for_uuids, latest_reports
from model.actions import copy_source, move_item
from model.queries import is_password_parameter
from model.report import Report
from model.transformations import change_source_parameter
from utils.functions import check_url_availability, uuid
from utils.type import EditScope

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION


@bottle.post("/api/v3/source/new/<metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_new(metric_uuid: MetricId, database: Database):
    """Add a new source."""
    all_reports = latest_reports(database)
    report = latest_report_for_uuids(all_reports, metric_uuid)[0]
    metric, subject = report.instance_and_parents_for_uuid(metric_uuid=metric_uuid)
    source_type = dict(bottle.request.json)["type"]
    parameters = default_source_parameters(database, metric.type(), source_type)
    metric.sources_dict[(source_uuid := uuid())] = {"type": source_type, "parameters": parameters}
    delta_description = (
        f"{{user}} added a new source to metric '{metric.name}' of subject "
        f"'{subject.name}' in report '{report.name}'."
    )
    uuids = [report.uuid, subject.uuid, metric.uuid, source_uuid]
    result = insert_new_report(database, delta_description, uuids, report)
    result["new_source_uuid"] = source_uuid
    return result


@bottle.post("/api/v3/source/<source_uuid>/copy/<metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_copy(source_uuid: SourceId, metric_uuid: MetricId, database: Database):
    """Add a copy of the source to the metric (new in v3)."""
    data_model = latest_datamodel(database)
    all_reports = latest_reports(database)
    reports = latest_report_for_uuids(all_reports, source_uuid, metric_uuid)
    source, source_metric, source_subject = reports[0].instance_and_parents_for_uuid(source_uuid=source_uuid)
    target_metric, target_subject = reports[1].instance_and_parents_for_uuid(metric_uuid=metric_uuid)

    target_metric["sources"][(source_copy_uuid := uuid())] = copy_source(source, data_model)
    delta_description = (
        f"{{user}} copied the source '{source.name}' of metric '{source_metric.name}' of subject "
        f"'{source_subject.name}' from report '{reports[0].name}' "
        f"to metric '{target_metric.name}' of subject "
        f"'{target_subject.name}' in report '{reports[1].name}'."
    )
    uuids = [reports[1].uuid, target_subject.uuid, target_metric.uuid, source_copy_uuid]
    result = insert_new_report(database, delta_description, uuids, reports[1])
    result["new_source_uuid"] = source_copy_uuid
    return result


@bottle.post("/api/v3/source/<source_uuid>/move/<target_metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_move_source(source_uuid: SourceId, target_metric_uuid: MetricId, database: Database):
    """Move the source to another metric."""
    all_reports = latest_reports(database)
    reports = latest_report_for_uuids(all_reports, source_uuid, target_metric_uuid)
    source, source_metric, source_subject = reports[0].instance_and_parents_for_uuid(source_uuid=source_uuid)
    target_metric, target_subject = reports[1].instance_and_parents_for_uuid(metric_uuid=target_metric_uuid)

    delta_description = (
        f"{{user}} moved the source '{source.name}' from metric '{source_metric.name}' of subject "
        f"'{source_subject.name}' in report '{reports[0].name}' "
        f"to metric '{target_metric.name}' of subject "
        f"'{target_subject.name}' in report '{reports[1].name}'."
    )
    target_metric["sources"][source_uuid] = source
    uuids: list[ItemId] = [
        reports[1].uuid,
        target_subject.uuid,
        target_metric_uuid,
        reports[0].uuid,
        source_subject.uuid,
        source_metric.uuid,
        source_uuid,
    ]
    reports_to_insert = [reports[1]]
    if reports[1] == reports[0]:
        # Source is moved within the same report
        del reports[1]["subjects"][source_subject.uuid]["metrics"][source_metric.uuid]["sources"][source_uuid]
    else:
        # Source is moved from one report to another, update both
        del source_metric["sources"][source_uuid]
        reports_to_insert.append(reports[0])
    return insert_new_report(database, delta_description, uuids, *reports_to_insert)


@bottle.delete("/api/v3/source/<source_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def delete_source(source_uuid: SourceId, database: Database):
    """Delete a source."""
    reports = latest_reports(database)
    report = latest_report_for_uuids(reports, source_uuid)[0]
    source, metric, subject = report.instance_and_parents_for_uuid(source_uuid=source_uuid)
    delta_description = (
        f"{{user}} deleted the source '{source.name}' from metric "
        f"'{metric.name}' of subject '{subject.name}' in report '{report.name}'."
    )
    uuids = [report.uuid, subject.uuid, metric.uuid, source_uuid]
    del metric["sources"][source_uuid]
    return insert_new_report(database, delta_description, uuids, report)


@bottle.post("/api/v3/source/<source_uuid>/attribute/<source_attribute>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_attribute(source_uuid: SourceId, source_attribute: str, database: Database):
    """Set a source attribute."""
    reports = latest_reports(database)
    report = latest_report_for_uuids(reports, source_uuid)[0]
    source, metric, subject = report.instance_and_parents_for_uuid(source_uuid=source_uuid)
    old_source_name = source.name  # in case the name is the attribute that is changed
    value = dict(bottle.request.json)[source_attribute]
    old_value: Any
    if source_attribute == "position":
        old_value, value = move_item(metric, source, value)
    else:
        old_value = source.get(source_attribute) or ""
        source[source_attribute] = value
    if old_value == value:
        return {"ok": True}  # Nothing to do
    delta_description = (
        f"{{user}} changed the {source_attribute} of source '{old_source_name}' of metric '{metric.name}' of "
        f"subject '{subject.name}' in report '{report.name}' from '{old_value}' to '{value}'."
    )
    uuids = [report.uuid, subject.uuid, metric.uuid, source.uuid]
    if source_attribute == "type":
        source["parameters"] = default_source_parameters(database, metric["type"], value)
    return insert_new_report(database, delta_description, uuids, report)


@bottle.post("/api/v3/source/<source_uuid>/parameter/<parameter_key>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_parameter(source_uuid: SourceId, parameter_key: str, database: Database):
    """Set the source parameter."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    items = _items(reports, source_uuid)
    new_value = new_parameter_value(data_model, items[0], parameter_key)
    old_value = items[0]["parameters"].get(parameter_key) or ""
    if old_value == new_value:
        return {"ok": True}  # Nothing to do
    edit_scope = cast(EditScope, dict(bottle.request.json).get("edit_scope", "source"))
    changed_ids, changed_source_ids = change_source_parameter(
        reports,
        items,
        parameter_key,
        old_value,
        new_value,
        edit_scope,
    )
    if is_password_parameter(data_model, items[0].type, parameter_key):
        new_value, old_value = "*" * len(new_value), "*" * len(old_value)
    source_description = _source_description(data_model, items, edit_scope, parameter_key, old_value)
    delta_description = (
        f"{{user}} changed the {parameter_key} of {source_description} from '{old_value}' to '{new_value}'."
    )
    reports_to_insert = [report for report in reports if report["report_uuid"] in changed_ids]
    result = insert_new_report(database, delta_description, changed_ids, *reports_to_insert)
    result["nr_sources_mass_edited"] = len(changed_source_ids) if edit_scope != "source" else 0
    result["availability"] = _availability_checks(data_model, items[0], parameter_key)
    return result


def _items(reports: list[Report], source_uuid: SourceId) -> tuple:
    """Return a tuple with all ancestors of the given source and the source itself."""
    report = latest_report_for_uuids(reports, source_uuid)[0]
    return (*report.instance_and_parents_for_uuid(source_uuid=source_uuid), report)


def new_parameter_value(data_model, source, parameter_key: str):
    """Return the new parameter value and if necessary, remove any obsolete multiple choice values."""
    new_value = dict(bottle.request.json)[parameter_key]
    source_parameter = data_model["sources"][source.type]["parameters"][parameter_key]
    if source_parameter["type"] == "multiple_choice":
        new_value = [value for value in new_value if value in source_parameter["values"]]
    return new_value


def _source_description(data_model, items, edit_scope, parameter_key, old_value) -> str:
    """Return the description of the source."""
    source, metric, subject, report = items
    source_type_name = data_model["sources"][source.type]["name"]
    source_description = (
        f"source '{source.name}'"
        if edit_scope == "source"
        else f"all sources of type '{source_type_name}' with {parameter_key} '{old_value}'"
    )
    if edit_scope in ["source", "metric"]:
        source_description += f" of metric '{metric.name}'"
    if edit_scope in ["subject", "metric", "source"]:
        source_description += f" of subject '{subject.name}'"
    source_description += " in all reports" if edit_scope == "reports" else f" in report '{report.name}'"
    return source_description


def _availability_checks(data_model, source, parameter_key: str) -> list[dict[str, str | int]]:
    """Check the availability of the URLs."""
    source_model = data_model["sources"][source["type"]]
    parameters = source_model["parameters"]
    token_validation_path = parameters.get("private_token", {}).get("validation_path", "")
    source_parameters = source["parameters"]
    url_parameter_keys = [
        key
        for key, value in parameters.items()
        if value["type"] == "url" and parameter_key == key or parameter_key in value.get("validate_on", [])
    ]
    availability_checks = []
    for url_parameter_key in url_parameter_keys:
        url = source_parameters.get(url_parameter_key, "")
        if not url:
            continue
        availability = check_url_availability(url, source_parameters, token_validation_path)
        availability["parameter_key"] = url_parameter_key
        availability["source_uuid"] = source.uuid
        availability_checks.append(availability)
    return availability_checks
