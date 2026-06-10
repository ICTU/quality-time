"""Source routes."""

from typing import Any, cast, TYPE_CHECKING

import bottle

from shared_data_model import DATA_MODEL
from shared_data_model.parameters import PrivateToken
from shared.model.source import Source
from shared.utils.type import SourceId

from database.reports import insert_new_report, latest_report_for_uuids, latest_reports
from model.actions import copy_source, import_referenced_source_locations, move_item
from model.defaults import default_source_parameters
from model.queries import is_password_parameter
from model.transformations import change_source_parameter, SOURCE_TYPES_WITHOUT_LOCATION
from utils.functions import check_url_availability, uuid
from utils.type import SourceContext

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION

if TYPE_CHECKING:
    from pymongo.database import Database

    from shared.utils.type import ItemId, MetricId, SourceLocationId

    from model.report import Report


@bottle.post("/api/internal/source/new/<metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_new(metric_uuid: MetricId, database: Database):
    """Add a new source."""
    all_reports = latest_reports(database)
    report = latest_report_for_uuids(all_reports, metric_uuid)[0]
    metric, subject = report.metric_and_subject(metric_uuid)
    source_type = dict(bottle.request.json)["type"]
    parameters = default_source_parameters(cast(str, metric.type()), source_type)
    source_uuid = cast(SourceId, uuid())
    source = cast(Source, {"type": source_type, "parameters": parameters})
    if source_type not in SOURCE_TYPES_WITHOUT_LOCATION:
        source["source_location"] = ""
    metric.sources_dict[source_uuid] = source
    delta_description = (
        f"{{user}} added a new source to metric '{metric.name}' of subject '{subject.name}' in report '{report.name}'."
    )
    uuids = [report.uuid, subject.uuid, metric.uuid, source_uuid]
    result = insert_new_report(database, delta_description, uuids, report)
    result["new_source_uuid"] = source_uuid
    return result


@bottle.post("/api/internal/source/<source_uuid>/copy/<metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_source_copy(source_uuid: SourceId, metric_uuid: MetricId, database: Database):
    """Add a copy of the source to the metric."""
    all_reports = latest_reports(database)
    reports = latest_report_for_uuids(all_reports, source_uuid, metric_uuid)
    source, source_metric, source_subject = reports[0].source_metric_and_subject(source_uuid)
    target_metric, target_subject = reports[1].metric_and_subject(metric_uuid)

    target_metric["sources"][(source_copy_uuid := uuid())] = copy_source(source_uuid, source)
    import_referenced_source_locations(reports[1], reports[0])
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


@bottle.post(
    "/api/internal/source/<source_uuid>/move/<target_metric_uuid>", permissions_required=[EDIT_REPORT_PERMISSION]
)
def post_move_source(source_uuid: SourceId, target_metric_uuid: MetricId, database: Database):
    """Move the source to another metric."""
    all_reports = latest_reports(database)
    reports = latest_report_for_uuids(all_reports, source_uuid, target_metric_uuid)
    source, source_metric, source_subject = reports[0].source_metric_and_subject(source_uuid)
    target_metric, target_subject = reports[1].metric_and_subject(target_metric_uuid)

    delta_description = (
        f"{{user}} moved the source '{source.name}' from metric '{source_metric.name}' of subject "
        f"'{source_subject.name}' in report '{reports[0].name}' "
        f"to metric '{target_metric.name}' of subject "
        f"'{target_subject.name}' in report '{reports[1].name}'."
    )
    target_metric["sources"][source_uuid] = source
    import_referenced_source_locations(reports[1], reports[0])
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


@bottle.delete("/api/internal/source/<source_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def delete_source(source_uuid: SourceId, database: Database):
    """Delete a source."""
    reports = latest_reports(database)
    report = latest_report_for_uuids(reports, source_uuid)[0]
    source, metric, subject = report.source_metric_and_subject(source_uuid)
    delta_description = (
        f"{{user}} deleted the source '{source.name}' from metric "
        f"'{metric.name}' of subject '{subject.name}' in report '{report.name}'."
    )
    uuids = [report.uuid, subject.uuid, metric.uuid, source_uuid]
    del metric["sources"][source_uuid]
    return insert_new_report(database, delta_description, uuids, report)


@bottle.post(
    "/api/internal/source/<source_uuid>/attribute/<source_attribute>", permissions_required=[EDIT_REPORT_PERMISSION]
)
def post_source_attribute(source_uuid: SourceId, source_attribute: str, database: Database):
    """Set a source attribute."""
    reports = latest_reports(database)
    report = latest_report_for_uuids(reports, source_uuid)[0]
    source, metric, subject = report.source_metric_and_subject(source_uuid)
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
    described_old_value, described_new_value = old_value, value
    if source_attribute == "source_location":
        described_old_value = _source_location_name(report, old_value)
        described_new_value = _source_location_name(report, value)
    delta_description = (
        f"{{user}} changed the {source_attribute} of source '{old_source_name}' of metric '{metric.name}' of "
        f"subject '{subject.name}' in report '{report.name}' from '{described_old_value}' to '{described_new_value}'."
    )
    uuids = [report.uuid, subject.uuid, metric.uuid, source.uuid]
    if source_attribute == "type":
        source["parameters"] = default_source_parameters(metric["type"], value)
        if value in SOURCE_TYPES_WITHOUT_LOCATION:
            source.pop("source_location", None)
        else:
            source["source_location"] = ""
    return insert_new_report(database, delta_description, uuids, report)


@bottle.post(
    "/api/internal/source/<source_uuid>/parameter/<parameter_key>", permissions_required=[EDIT_REPORT_PERMISSION]
)
def post_source_parameter(source_uuid: SourceId, parameter_key: str, database: Database):
    """Set the source parameter."""
    reports = latest_reports(database)
    context = get_source_context(reports, source_uuid)
    new_value = _new_parameter_value(context.source, parameter_key)
    old_value = context.source["parameters"].get(parameter_key) or ""
    if old_value == new_value:
        return {"ok": True}  # Nothing to do
    changed_ids = change_source_parameter(context, parameter_key, new_value)
    if is_password_parameter(context.source.type, parameter_key):
        new_value, old_value = "*" * len(new_value), "*" * len(old_value)
    delta_description = (
        f"{{user}} changed the {parameter_key} of source '{context.source.name}' of metric '{context.metric.name}' "
        f"of subject '{context.subject.name}' in report '{context.report.name}' "
        f"from '{old_value}' to '{new_value}'."
    )
    result = insert_new_report(database, delta_description, changed_ids, context.report)
    result["availability"] = availability_check(
        context.source["type"], context.source.parameters_including_location(), context.source.uuid, parameter_key
    )
    return result


def get_source_context(reports: list[Report], source_uuid: SourceId) -> SourceContext:
    """Return a source and its context, meaning the containing metric, subject, and report."""
    report = latest_report_for_uuids(reports, source_uuid)[0]
    source, metric, subject = report.source_metric_and_subject(source_uuid)
    return SourceContext(source=source, metric=metric, subject=subject, report=report)


def _source_location_name(report: Report, source_location_uuid: SourceLocationId) -> str:
    """Return the name of the source location to use in delta descriptions."""
    if not source_location_uuid:
        return ""
    source_location = report.source_locations_dict.get(source_location_uuid, {})
    if location_name := source_location.get("location_name"):
        return str(location_name)
    if source_type := source_location.get("source_type"):
        if source_type in DATA_MODEL.sources:
            return str(DATA_MODEL.sources[source_type].name)
        # Be prepared for source locations with a source type that is no longer part of the data model:
        return str(source_type)  # pragma: no feature-test-cover
    return ""  # pragma: no feature-test-cover


def _new_parameter_value(source: Source, parameter_key: str) -> str | list[str]:
    """Return the new parameter value and if necessary, remove any obsolete multiple choice values."""
    new_value = dict(bottle.request.json)[parameter_key]
    source_parameter = DATA_MODEL.sources[source.type].parameters[parameter_key]
    if source_parameter.type in ("multiple_choice_with_defaults", "multiple_choice_without_defaults"):
        new_value = [value for value in new_value if value in (source_parameter.values or [])]
    return cast(str, new_value)


def availability_check(
    source_type: str,
    parameters: dict,
    identifier: SourceId | str,
    parameter_key: str,
) -> dict[str, str | int]:
    """Check the availability of the URL affected by a change to parameter_key, if any."""
    data_model_parameters = DATA_MODEL.sources[source_type].parameters
    url_parameter_key = next(
        (
            key
            for key, value in data_model_parameters.items()
            if (value.type == "url" and parameter_key == key) or parameter_key in (value.validate_on or [])
        ),
        None,
    )
    if not url_parameter_key or not (url := parameters.get(url_parameter_key)):
        return {}
    private_token = cast(PrivateToken, data_model_parameters.get("private_token"))
    token_validation_path = private_token.validation_path if private_token else ""
    availability = check_url_availability(url, parameters, token_validation_path)
    availability["parameter_key"] = url_parameter_key
    availability["source_uuid"] = identifier
    return availability
