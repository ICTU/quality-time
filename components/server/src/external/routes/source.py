"""Source routes."""

from typing import Any, cast

import bottle
from pymongo.database import Database

from database.reports import latest_reports
from server_utilities.type import MetricId, ReportId, SourceId, SubjectId

from ..database.datamodels import default_source_parameters, latest_datamodel
from ..database.reports import insert_new_report
from ..model.actions import copy_source, move_item
from ..model.data import MetricData, SourceData
from ..model.queries import is_password_parameter
from ..model.transformations import change_source_parameter
from ..utils.functions import check_url_availability, uuid
from ..utils.type import EditScope

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION


@bottle.post("/api/v3/source/new/<metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_new(metric_uuid: MetricId, database: Database):
    """Add a new source."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    data = MetricData(data_model, reports, metric_uuid)
    metric_type = data.metric["type"]
    source_type = data_model["metrics"][metric_type]["default_source"]
    parameters = default_source_parameters(database, metric_type, source_type)
    data.metric["sources"][(source_uuid := uuid())] = dict(type=source_type, parameters=parameters)
    delta_description = (
        f"{{user}} added a new source to metric '{data.metric_name}' of subject "
        f"'{data.subject_name}' in report '{data.report_name}'."
    )
    uuids = [data.report_uuid, data.subject_uuid, metric_uuid, source_uuid]
    result = insert_new_report(database, delta_description, uuids, data.report)
    result["new_source_uuid"] = source_uuid
    return result


@bottle.post("/api/v3/source/<source_uuid>/copy/<metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_copy(source_uuid: SourceId, metric_uuid: MetricId, database: Database):
    """Add a copy of the source to the metric (new in v3)."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    source = SourceData(data_model, reports, source_uuid)
    target = MetricData(data_model, reports, metric_uuid)
    target.metric["sources"][(source_copy_uuid := uuid())] = copy_source(source.source, source.datamodel)
    delta_description = (
        f"{{user}} copied the source '{source.source_name}' of metric '{source.metric_name}' of subject "
        f"'{source.subject_name}' from report '{source.report_name}' to metric '{target.metric_name}' of subject "
        f"'{target.subject_name}' in report '{target.report_name}'."
    )
    uuids = [target.report_uuid, target.subject_uuid, target.metric_uuid, source_copy_uuid]
    result = insert_new_report(database, delta_description, uuids, target.report)
    result["new_source_uuid"] = source_copy_uuid
    return result


@bottle.post("/api/v3/source/<source_uuid>/move/<target_metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_move_source(source_uuid: SourceId, target_metric_uuid: MetricId, database: Database):
    """Move the source to another metric."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    source = SourceData(data_model, reports, source_uuid)
    target = MetricData(data_model, reports, target_metric_uuid)
    delta_description = (
        f"{{user}} moved the source '{source.source_name}' from metric '{source.metric_name}' of subject "
        f"'{source.subject_name}' in report '{source.report_name}' to metric '{target.metric_name}' of subject "
        f"'{target.subject_name}' in report '{target.report_name}'."
    )
    target.metric["sources"][source_uuid] = source.source
    uuids: list[ReportId | SubjectId | MetricId | SourceId | None] = [
        target.report_uuid,
        target.subject_uuid,
        target_metric_uuid,
        source.report_uuid,
        source.subject_uuid,
        source.metric_uuid,
        source_uuid,
    ]
    reports_to_insert = [target.report]
    if target.report_uuid == source.report_uuid:
        # Source is moved within the same report
        del target.report["subjects"][source.subject_uuid]["metrics"][source.metric_uuid]["sources"][source_uuid]
    else:
        # Source is moved from one report to another, update both
        del source.metric["sources"][source_uuid]
        reports_to_insert.append(source.report)
    return insert_new_report(database, delta_description, uuids, *reports_to_insert)


@bottle.delete("/api/v3/source/<source_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def delete_source(source_uuid: SourceId, database: Database):
    """Delete a source."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    data = SourceData(data_model, reports, source_uuid)
    delta_description = (
        f"{{user}} deleted the source '{data.source_name}' from metric "
        f"'{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}'."
    )
    uuids = [data.report_uuid, data.subject_uuid, data.metric_uuid, source_uuid]
    del data.metric["sources"][source_uuid]
    return insert_new_report(database, delta_description, uuids, data.report)


@bottle.post("/api/v3/source/<source_uuid>/attribute/<source_attribute>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_attribute(source_uuid: SourceId, source_attribute: str, database: Database):
    """Set a source attribute."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    data = SourceData(data_model, reports, source_uuid)
    value = dict(bottle.request.json)[source_attribute]
    old_value: Any
    if source_attribute == "position":
        old_value, value = move_item(data, value, "source")
    else:
        old_value = data.source.get(source_attribute) or ""
        data.source[source_attribute] = value
    if old_value == value:
        return dict(ok=True)  # Nothing to do
    delta_description = (
        f"{{user}} changed the {source_attribute} of source '{data.source_name}' of metric '{data.metric_name}' of "
        f"subject '{data.subject_name}' in report '{data.report_name}' from '{old_value}' to '{value}'."
    )
    uuids = [data.report_uuid, data.subject_uuid, data.metric_uuid, source_uuid]
    if source_attribute == "type":
        data.source["parameters"] = default_source_parameters(database, data.metric["type"], value)
    return insert_new_report(database, delta_description, uuids, data.report)


@bottle.post("/api/v3/source/<source_uuid>/parameter/<parameter_key>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_parameter(source_uuid: SourceId, parameter_key: str, database: Database):
    """Set the source parameter."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    data = SourceData(data_model, reports, source_uuid)
    new_value = new_parameter_value(data, parameter_key)
    old_value = data.source["parameters"].get(parameter_key) or ""
    if old_value == new_value:
        return dict(ok=True)  # Nothing to do
    edit_scope = cast(EditScope, dict(bottle.request.json).get("edit_scope", "source"))
    changed_ids = change_source_parameter(data, parameter_key, old_value, new_value, edit_scope)

    if is_password_parameter(data.datamodel, data.source["type"], parameter_key):
        new_value, old_value = "*" * len(new_value), "*" * len(old_value)

    source_description = _source_description(data, edit_scope, parameter_key, old_value)
    delta_description = (
        f"{{user}} changed the {parameter_key} of {source_description} from '{old_value}' to '{new_value}'."
    )
    reports_to_insert = [report for report in data.reports if report["report_uuid"] in changed_ids]
    result = insert_new_report(database, delta_description, changed_ids, *reports_to_insert)

    if availability_checks := _availability_checks(data, parameter_key):
        result["availability"] = availability_checks
    return result


def new_parameter_value(data, parameter_key: str):
    """Return the new parameter value and if necessary, remove any obsolete multiple choice values."""
    new_value = dict(bottle.request.json)[parameter_key]
    source_parameter = data.datamodel["sources"][data.source["type"]]["parameters"][parameter_key]
    if source_parameter["type"] == "multiple_choice":
        new_value = [value for value in new_value if value in source_parameter["values"]]
    return new_value


def _source_description(data, edit_scope, parameter_key, old_value):
    """Return the description of the source."""
    source_type_name = data.datamodel["sources"][data.source["type"]]["name"]
    source_description = (
        f"source '{data.source_name}'"
        if edit_scope == "source"
        else f"all sources of type '{source_type_name}' with {parameter_key} '{old_value}'"
    )
    if edit_scope in ["source", "metric"]:
        source_description += f" of metric '{data.metric_name}'"
    if edit_scope in ["subject", "metric", "source"]:
        source_description += f" of subject '{data.subject_name}'"
    source_description += " in all reports" if edit_scope == "reports" else f" in report '{data.report_name}'"
    return source_description


def _availability_checks(data, parameter_key: str) -> list[dict[str, str | int]]:
    """Check the availability of the URLs."""
    parameters = data.datamodel["sources"][data.source["type"]]["parameters"]
    source_parameters = data.source["parameters"]
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
        availability = check_url_availability(url, source_parameters)
        availability["parameter_key"] = url_parameter_key
        availability["source_uuid"] = data.source_uuid
        availability_checks.append(availability)
    return availability_checks
