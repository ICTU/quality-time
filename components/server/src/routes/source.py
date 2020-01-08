"""Source routes."""

from typing import Any, Dict, List, Tuple, Optional, Union

import bottle
import requests
from pymongo.database import Database

from database import sessions
from database.datamodels import latest_datamodel, default_source_parameters
from database.reports import get_data, insert_new_report
from model.actions import copy_source, move_item
from server_utilities.functions import uuid
from server_utilities.type import MetricId, ReportId, SourceId, URL


@bottle.post("/api/v1/report/<report_uuid>/metric/<metric_uuid>/source/new")
def post_source_new_v1(report_uuid: ReportId, metric_uuid: MetricId, database: Database):
    """Add a new source."""
    # pylint: disable=unused-argument
    return post_source_new(metric_uuid, database)  # pragma: nocover


@bottle.post("/api/v2/source/new/<metric_uuid>")
def post_source_new(metric_uuid: MetricId, database: Database):
    """Add a new source."""
    data = get_data(database, metric_uuid=metric_uuid)
    data_model = latest_datamodel(database)
    metric_type = data.metric["type"]
    source_type = data_model["metrics"][metric_type]["default_source"]
    parameters = default_source_parameters(database, metric_type, source_type)
    data.metric["sources"][uuid()] = dict(type=source_type, parameters=parameters)
    data.report["delta"] = dict(
        report_uuid=data.report_uuid, subject_uuid=data.subject_uuid, metric_uuid=metric_uuid,
        description=f"{sessions.user(database)} added a new source to metric '{data.metric_name}' of subject "
                    f"'{data.subject_name}' in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/source/<source_uuid>/copy")
def post_source_copy_v1(report_uuid: ReportId, source_uuid: SourceId, database: Database):
    """Copy a source."""
    # pylint: disable=unused-argument
    return post_source_copy(source_uuid, database)  # pragma: nocover


@bottle.post("/api/v2/source/<source_uuid>/copy")
def post_source_copy(source_uuid: SourceId, database: Database):
    """Copy a source."""
    data = get_data(database, source_uuid=source_uuid)
    data.metric["sources"][uuid()] = copy_source(data.source, data.datamodel)
    data.report["delta"] = dict(
        report_uuid=data.report_uuid, subject_uuid=data.subject_uuid, metric_uuid=data.metric_uuid,
        description=f"{sessions.user(database)} copied the source '{data.source_name}' of metric "
                    f"'{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.delete("/api/v1/report/<report_uuid>/source/<source_uuid>")
def delete_source_v1(report_uuid: ReportId, source_uuid: SourceId, database: Database):
    """Delete a source."""
    # pylint: disable=unused-argument
    return delete_source(source_uuid, database)  # pragma: nocover


@bottle.delete("/api/v2/source/<source_uuid>")
def delete_source(source_uuid: SourceId, database: Database):
    """Delete a source."""
    data = get_data(database, source_uuid=source_uuid)
    data.report["delta"] = dict(
        report_uuid=data.report_uuid, subject_uuid=data.subject_uuid, metric_uuid=data.metric_uuid,
        description=f"{sessions.user(database)} deleted the source '{data.source_name}' from metric "
                    f"'{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}'.")
    del data.metric["sources"][source_uuid]
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/source/<source_uuid>/<source_attribute>")
def post_source_attribute_v1(report_uuid: ReportId, source_uuid: SourceId, source_attribute: str, database: Database):
    """Set a source attribute."""
    # pylint: disable=unused-argument
    return post_source_attribute(source_uuid, source_attribute, database)  # pragma: nocover


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
    data.report["delta"] = dict(
        report_uuid=data.report_uuid, subject_uuid=data.subject_uuid, metric_uuid=data.metric_uuid,
        source_uuid=source_uuid,
        description=f"{sessions.user(database)} changed the {source_attribute} of source '{data.source_name}' of "
                    f"metric '{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}' "
                    f"from '{old_value}' to '{value}'.")
    if source_attribute == "type":
        data.source["parameters"] = default_source_parameters(database, data.metric["type"], value)
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/source/<source_uuid>/parameter/<parameter_key>")
def post_source_parameter_v1(report_uuid: ReportId, source_uuid: SourceId, parameter_key: str, database: Database):
    """Set a source parameter."""
    # pylint: disable=unused-argument
    return post_source_parameter(source_uuid, parameter_key, database)  # pragma: nocover


@bottle.post("/api/v2/source/<source_uuid>/parameter/<parameter_key>")
def post_source_parameter(source_uuid: SourceId, parameter_key: str, database: Database):
    """Set the source parameter."""
    data = get_data(database, source_uuid=source_uuid)
    new_value = dict(bottle.request.json)[parameter_key]
    old_value = data.source["parameters"].get(parameter_key) or ""
    if old_value == new_value:
        return dict(ok=True)  # Nothing to do
    data.source["parameters"][parameter_key] = new_value
    if data.datamodel["sources"][data.source["type"]]["parameters"][parameter_key]["type"] == "password":
        new_value, old_value = "*" * len(new_value), "*" * len(old_value)

    data.report["delta"] = dict(
        report_uuid=data.report_uuid, subject_uuid=data.subject_uuid, metric_uuid=data.metric_uuid,
        source_uuid=source_uuid,
        description=f"{sessions.user(database)} changed the {parameter_key} of source '{data.source_name}' of metric "
                    f"'{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}' from "
                    f"'{old_value}' to '{new_value}'.")

    result = insert_new_report(database, data.report)

    parameters = data.datamodel["sources"][data.source["type"]]["parameters"]

    urls_param_keys = [param_key for param_key in parameters
                       if parameters[param_key]['type'] == 'url' and parameter_key == param_key or
                       ("validate_on" in parameters[param_key] and parameter_key in
                        parameters[param_key]["validate_on"].split(','))]

    if availability_checks := _availability_checks(urls_param_keys, data.source["parameters"], source_uuid):
        result["availability"] = availability_checks
    return result


def _check_url_availability(url: URL, source_parameters: Dict[str, str]) -> Dict[str, Union[int, str]]:
    """Check the availability of the URL."""
    try:
        response = requests.get(url, auth=_basic_auth_credentials(source_parameters))
        return dict(status_code=response.status_code, reason=response.reason)
    except Exception:  # pylint: disable=broad-except
        return dict(status_code=-1, reason='Unknown error')


def _availability_checks(url_parameter_keys, source_parameters, source_uuid) -> List[Dict[str, Union[str, int]]]:
    """Check the availability of the URLs."""
    availability_checks = []
    for url_parameter_key in url_parameter_keys:
        url = source_parameters.get(url_parameter_key, "")
        if not url:
            continue
        availability = _check_url_availability(url, source_parameters)
        availability['parameter_key'] = url_parameter_key
        availability['source_uuid'] = source_uuid
        availability_checks.append(availability)
    return availability_checks


def _basic_auth_credentials(source_parameters) -> Optional[Tuple[str, str]]:
    """Return the basic authentication credentials, if any."""
    if "private_token" in source_parameters:
        return source_parameters["private_token"], ""
    if "username" in source_parameters and "password" in source_parameters:
        return source_parameters["username"], source_parameters["password"]
    return None
