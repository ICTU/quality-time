"""Source routes."""

from typing import cast, Any, Dict, List, Tuple, Optional, Union

import bottle
import requests
from pymongo.database import Database

from database import sessions
from database.datamodels import latest_datamodel, default_source_parameters
from database.reports import get_data, insert_new_report
from model.actions import copy_source, move_item
from model.transformations import change_source_parameter
from model.queries import is_password_parameter
from server_utilities.functions import uuid
from server_utilities.type import EditScope, MetricId, SourceId, URL


@bottle.post("/api/v2/source/new/<metric_uuid>")
def post_source_new(metric_uuid: MetricId, database: Database):
    """Add a new source."""
    data = get_data(database, metric_uuid=metric_uuid)
    data_model = latest_datamodel(database)
    metric_type = data.metric["type"]
    source_type = data_model["metrics"][metric_type]["default_source"]
    parameters = default_source_parameters(database, metric_type, source_type)
    data.metric["sources"][(source_uuid := uuid())] = dict(type=source_type, parameters=parameters)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, metric_uuid, source_uuid], email=user["email"],
        description=f"{user['user']} added a new source to metric '{data.metric_name}' of subject "
                    f"'{data.subject_name}' in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v2/source/<source_uuid>/copy")
def post_source_copy(source_uuid: SourceId, database: Database):
    """Copy a source."""
    data = get_data(database, source_uuid=source_uuid)
    data.metric["sources"][(source_copy_uuid := uuid())] = copy_source(data.source, data.datamodel)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, data.metric_uuid, source_uuid, source_copy_uuid],
        email=user["email"],
        description=f"{user['user']} copied the source '{data.source_name}' of metric "
                    f"'{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v2/source/<source_uuid>/move/<target_metric_uuid>")
def post_move_source(source_uuid: SourceId, target_metric_uuid: MetricId, database: Database):
    """Move the source to another metric."""
    source = get_data(database, source_uuid=source_uuid)
    target = get_data(database, metric_uuid=target_metric_uuid)
    user = sessions.user(database)
    delta_description = f"{user['user']} moved the source '{source.source_name}' from metric " \
                        f"'{source.metric_name}' of subject '{source.subject_name}' in report '{source.report_name}' " \
                        f"to metric '{target.metric_name}' of subject '{target.subject_name}' in report " \
                        f"'{target.report_name}'."
    target.metric["sources"][source_uuid] = source.source
    target_uuids = [target.report_uuid]
    if target.report_uuid == source.report_uuid:
        # Source is moved within the same report
        del target.report["subjects"][source.subject_uuid]["metrics"][source.metric_uuid]["sources"][source_uuid]
        if target.subject_uuid != source.subject_uuid:
            # Source is moved from one subject to another subject, include both subject uuids in the delta
            target_uuids.append(source.subject_uuid)
        target_uuids.extend([target.subject_uuid, source.metric_uuid])
    else:
        # Source is move from one report to another, update both
        del source.metric["sources"][source_uuid]
        source.report["delta"] = dict(
            uuids=[source.report_uuid, source.subject_uuid, source.metric_uuid, source_uuid], email=user["email"],
            description=delta_description)
        target_uuids.append(target.subject_uuid)
    target.report["delta"] = dict(
        uuids=target_uuids + [target_metric_uuid, source_uuid], email=user["email"], description=delta_description)
    return insert_new_report(database, source.report, target.report)


@bottle.delete("/api/v2/source/<source_uuid>")
def delete_source(source_uuid: SourceId, database: Database):
    """Delete a source."""
    data = get_data(database, source_uuid=source_uuid)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, data.metric_uuid, source_uuid], email=user["email"],
        description=f"{user['user']} deleted the source '{data.source_name}' from metric "
                    f"'{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}'.")
    del data.metric["sources"][source_uuid]
    return insert_new_report(database, data.report)


@bottle.post("/api/v2/source/<source_uuid>/attribute/<source_attribute>")
def post_source_attribute(source_uuid: SourceId, source_attribute: str, database: Database):
    """Set a source attribute."""
    data = get_data(database, source_uuid=source_uuid)
    value = dict(bottle.request.json)[source_attribute]
    old_value: Any
    if source_attribute == "position":
        old_value, value = move_item(data, value, "source")
    else:
        old_value = data.source.get(source_attribute) or ""
        data.source[source_attribute] = value
    if old_value == value:
        return dict(ok=True)  # Nothing to do
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, data.metric_uuid, source_uuid], email=user["email"],
        description=f"{user['user']} changed the {source_attribute} of source '{data.source_name}' "
                    f"of metric '{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}' "
                    f"from '{old_value}' to '{value}'.")
    if source_attribute == "type":
        data.source["parameters"] = default_source_parameters(database, data.metric["type"], value)
    return insert_new_report(database, data.report)


@bottle.post("/api/v2/source/<source_uuid>/parameter/<parameter_key>")
def post_source_parameter(source_uuid: SourceId, parameter_key: str, database: Database):
    """Set the source parameter."""
    data = get_data(database, source_uuid=source_uuid)
    new_value = dict(bottle.request.json)[parameter_key]
    old_value = data.source["parameters"].get(parameter_key) or ""
    if old_value == new_value:
        return dict(ok=True)  # Nothing to do
    edit_scope = cast(EditScope, dict(bottle.request.json).get("edit_scope", "source"))
    changed_ids = change_source_parameter(data, parameter_key, old_value, new_value, edit_scope)

    if is_password_parameter(data.datamodel, data.source["type"], parameter_key):
        new_value, old_value = "*" * len(new_value), "*" * len(old_value)

    source_description = _source_description(data, edit_scope, parameter_key, old_value)
    user = sessions.user(database)
    delta = dict(
        uuids=changed_ids, email=user["email"],
        description=f"{user['user']} changed the {parameter_key} of {source_description} "
                    f"from '{old_value}' to '{new_value}'.")
    reports_to_insert = [report for report in data.reports if report["report_uuid"] in changed_ids]
    for report in reports_to_insert:
        report["delta"] = delta
    result = insert_new_report(database, *reports_to_insert)

    if availability_checks := _availability_checks(data, parameter_key):
        result["availability"] = availability_checks
    return result


def _source_description(data, edit_scope, parameter_key, old_value):
    """Return the description of the source."""
    source_type_name = data.datamodel["sources"][data.source["type"]]["name"]
    source_description = f"source '{data.source_name}'" if edit_scope == "source" else \
        f"all sources of type '{source_type_name}' with {parameter_key} '{old_value}'"
    if edit_scope in ["source", "metric"]:
        source_description += f" of metric '{data.metric_name}'"
    if edit_scope in ["subject", "metric", "source"]:
        source_description += f" of subject '{data.subject_name}'"
    source_description += " in all reports" if edit_scope == "reports" else f" in report '{data.report_name}'"
    return source_description


def _availability_checks(data, parameter_key: str) -> List[Dict[str, Union[str, int]]]:
    """Check the availability of the URLs."""
    parameters = data.datamodel["sources"][data.source["type"]]["parameters"]
    source_parameters = data.source["parameters"]
    url_parameter_keys = [
        key for key, value in parameters.items()
        if value['type'] == 'url' and parameter_key == key or parameter_key in value.get("validate_on", [])]
    availability_checks = []
    for url_parameter_key in url_parameter_keys:
        url = source_parameters.get(url_parameter_key, "")
        if not url:
            continue
        availability = _check_url_availability(url, source_parameters)
        availability['parameter_key'] = url_parameter_key
        availability['source_uuid'] = data.source_uuid
        availability_checks.append(availability)
    return availability_checks


def _check_url_availability(url: URL, source_parameters: Dict[str, str]) -> Dict[str, Union[int, str]]:
    """Check the availability of the URL."""
    try:
        response = requests.get(
            url, auth=_basic_auth_credentials(source_parameters), headers=_headers(source_parameters))
        return dict(status_code=response.status_code, reason=response.reason)
    except Exception:  # pylint: disable=broad-except
        return dict(status_code=-1, reason='Unknown error')


def _basic_auth_credentials(source_parameters) -> Optional[Tuple[str, str]]:
    """Return the basic authentication credentials, if any."""
    if private_token := source_parameters.get("private_token", ""):
        return private_token, ""
    username = source_parameters.get("username", "")
    password = source_parameters.get("password", "")
    return (username, password) if username and password else None


def _headers(source_parameters) -> Dict:
    """Return the headers for the url-check."""
    return {"Private-Token": source_parameters["private_token"]} if "private_token" in source_parameters else dict()
