"""Source location routes."""

from http import HTTPStatus
from typing import cast, TYPE_CHECKING

import bottle

from shared.model.source import LOCATION_PARAMETERS, PASSWORD_PARAMETERS
from shared_data_model import DATA_MODEL

from database.reports import insert_new_report, latest_report_for_uuids, latest_reports
from model.transformations import CREDENTIALS_REPLACEMENT_TEXT, SOURCE_TYPES_WITHOUT_LOCATION
from utils.functions import uuid

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION
from .report import with_report
from .source import availability_check

if TYPE_CHECKING:
    from pymongo.database import Database

    from shared.utils.type import ItemId, SourceLocationId

    from model.report import Report


@bottle.post("/api/internal/source_location/new/<report_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
@with_report(pass_report_uuid=False)
def post_source_location_new(database: Database, report: Report):
    """Add a new source location to the report."""
    source_type = dict(bottle.request.json)["type"]
    if source_type not in DATA_MODEL.sources or source_type in SOURCE_TYPES_WITHOUT_LOCATION:
        return {"ok": False, "error": f"Source type '{source_type}' does not have source locations."}
    source_location_uuid = cast("SourceLocationId", uuid())
    source_location = {"location_name": "", "source_type": source_type}
    for parameter_key in LOCATION_PARAMETERS:
        source_location[parameter_key] = ""
    report.setdefault("source_locations", {})[source_location_uuid] = source_location
    source_type_name = DATA_MODEL.sources[source_type].name
    delta_description = f"{{user}} added a new source location of type '{source_type_name}' to report '{report.name}'."
    uuids: list[ItemId] = [report.uuid, source_location_uuid]
    result = insert_new_report(database, delta_description, uuids, report)
    result["new_source_location_uuid"] = source_location_uuid
    return result


@bottle.get("/api/internal/source_location/<source_location_uuid>", authentication_required=False)
def get_source_location(source_location_uuid: SourceLocationId, database: Database):
    """Return the source location, with the credentials hidden."""
    result = _source_location_and_report(database, source_location_uuid)
    if result is None:
        return _missing_source_location(source_location_uuid)
    source_location, _report = result
    source_location = dict(source_location)
    for parameter_key in PASSWORD_PARAMETERS:
        if source_location.get(parameter_key):
            source_location[parameter_key] = CREDENTIALS_REPLACEMENT_TEXT
    return {"ok": True, "source_location_uuid": source_location_uuid, "source_location": source_location}


@bottle.post(
    "/api/internal/source_location/<source_location_uuid>/attribute/<source_location_attribute>",
    permissions_required=[EDIT_REPORT_PERMISSION],
)
def post_source_location_attribute(
    source_location_uuid: SourceLocationId, source_location_attribute: str, database: Database
):
    """Set a source location attribute."""
    result = _source_location_and_report(database, source_location_uuid)
    if result is None:  # pragma: no feature-test-cover
        return _missing_source_location(source_location_uuid)
    source_location, report = result
    old_location_name = source_location_name(source_location)
    value = dict(bottle.request.json)[source_location_attribute]
    old_value = source_location.get(source_location_attribute) or ""
    if old_value == value:
        return {"ok": True}  # Nothing to do
    source_location[source_location_attribute] = value
    delta_description = (
        f"{{user}} changed the {source_location_attribute} of source location '{old_location_name}' in report "
        f"'{report.name}' from '{old_value}' to '{value}'."
    )
    uuids: list[ItemId] = [
        report.uuid,
        source_location_uuid,
        *_uuids_of_referencing_sources(report, source_location_uuid),
    ]
    return insert_new_report(database, delta_description, uuids, report)


@bottle.post(
    "/api/internal/source_location/<source_location_uuid>/parameter/<parameter_key>",
    permissions_required=[EDIT_REPORT_PERMISSION],
)
def post_source_location_parameter(source_location_uuid: SourceLocationId, parameter_key: str, database: Database):
    """Set a source location parameter."""
    if parameter_key not in LOCATION_PARAMETERS:
        return {"ok": False, "error": f"Parameter '{parameter_key}' is not a source location parameter."}
    result = _source_location_and_report(database, source_location_uuid)
    if result is None:  # pragma: no feature-test-cover
        return _missing_source_location(source_location_uuid)
    source_location, report = result
    new_value = dict(bottle.request.json)[parameter_key]
    old_value = source_location.get(parameter_key) or ""
    if old_value == new_value:
        return {"ok": True}  # Nothing to do
    source_location[parameter_key] = new_value
    described_old_value, described_new_value = old_value, new_value
    if parameter_key in PASSWORD_PARAMETERS:
        described_old_value, described_new_value = "*" * len(old_value), "*" * len(new_value)
    delta_description = (
        f"{{user}} changed the {parameter_key} of source location '{source_location_name(source_location)}' "
        f"in report '{report.name}' from '{described_old_value}' to '{described_new_value}'."
    )
    uuids: list[ItemId] = [
        report.uuid,
        source_location_uuid,
        *_uuids_of_referencing_sources(report, source_location_uuid),
    ]
    insert_result = insert_new_report(database, delta_description, uuids, report)
    insert_result["availability"] = availability_check(
        source_location["source_type"], source_location, source_location_uuid, parameter_key
    )
    return insert_result


@bottle.delete("/api/internal/source_location/<source_location_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def delete_source_location(source_location_uuid: SourceLocationId, database: Database):
    """Delete a source location, unless it is in use by one or more sources."""
    result = _source_location_and_report(database, source_location_uuid)
    if result is None:  # pragma: no feature-test-cover
        return _missing_source_location(source_location_uuid)
    source_location, report = result
    if _uuids_of_referencing_sources(report, source_location_uuid):
        return {
            "ok": False,
            "error": f"Source location with UUID {source_location_uuid} is in use by one or more sources.",
        }
    delta_description = (
        f"{{user}} deleted the source location '{source_location_name(source_location)}' from report '{report.name}'."
    )
    uuids: list[ItemId] = [report.uuid, source_location_uuid]
    del report["source_locations"][source_location_uuid]
    return insert_new_report(database, delta_description, uuids, report)


def source_location_name(source_location: dict) -> str:
    """Return the name of the source location to use in delta descriptions."""
    if location_name := source_location.get("location_name"):
        return str(location_name)
    source_type = source_location.get("source_type", "")
    if source_type in DATA_MODEL.sources:
        return str(DATA_MODEL.sources[source_type].name)
    # Be prepared for source locations with a source type that is no longer part of the data model:
    return str(source_type)  # pragma: no feature-test-cover


def _source_location_and_report(
    database: Database, source_location_uuid: SourceLocationId
) -> tuple[dict, Report] | None:
    """Return the source location and the report it belongs to, or None if it can't be found."""
    reports = latest_report_for_uuids(latest_reports(database), source_location_uuid)
    if not reports:
        return None
    report = reports[0]
    return report.source_locations_dict[source_location_uuid], report


def _missing_source_location(source_location_uuid: SourceLocationId) -> dict[str, str | bool]:
    """Return an error response for a missing source location."""
    bottle.response.status = HTTPStatus.NOT_FOUND
    return {"ok": False, "error": f"Source location with UUID {source_location_uuid} not found."}


def _uuids_of_referencing_sources(report: Report, source_location_uuid: SourceLocationId) -> list[ItemId]:
    """Return the uuids of the subjects, metrics, and sources of the sources that use the source location."""
    uuids: list[ItemId] = []
    for source_uuid, source in report.sources_dict.items():
        if source.get("source_location") == source_location_uuid:
            uuids.extend([source.metric.subject_uuid, source.metric.uuid, source_uuid])
    return uuids
