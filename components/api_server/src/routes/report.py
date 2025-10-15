"""Report routes."""

from functools import partial, wraps
from http import HTTPStatus
from typing import cast, TYPE_CHECKING

import bottle

from shared_data_model import DATA_MODEL
from shared_data_model.parameters import PrivateToken

from database.datamodels import latest_datamodel
from database.measurements import recent_measurements
from database.reports import insert_new_report, latest_report, latest_reports_before_timestamp
from initialization.app_secrets import EXPORT_FIELDS_KEYS_NAME
from model.actions import copy_report
from model.defaults import default_report_attributes
from model.transformations import (
    decrypt_credentials,
    encrypt_credentials,
    hide_credentials,
    replace_report_uuids,
)
from utils.functions import DecryptionError, check_url_availability, report_date_time, sanitize_html, uuid

from .pdf import export_as_pdf
from .plugins.auth_plugin import EDIT_REPORT_PERMISSION

if TYPE_CHECKING:
    from collections.abc import Callable

    from pymongo.database import Database

    from shared.utils.type import ReportId

    from model.report import Report


def with_report[ReturnType](route: Callable[..., ReturnType] | None = None, pass_report_uuid: bool = True):
    """Return a decorator to fetch a report from the database and pass it to the route, or bail if it can't be found."""
    if route is None:  # Allow for using the decorator without brackets, e.g. @with_report
        return partial(with_report, pass_report_uuid=pass_report_uuid)

    @wraps(route)
    def wrapper(database: Database, report_uuid: ReportId, *args, **kwargs) -> ReturnType | dict[str, str | bool]:
        report = latest_report(database, report_uuid)
        if report is None:
            bottle.response.status = HTTPStatus.NOT_FOUND
            return {"ok": False, "error": f"Report with UUID {report_uuid} not found."}
        route_args: list[Report | ReportId | Database] = [database, report]
        if pass_report_uuid:
            route_args.append(report_uuid)
        route_args.extend(args)
        return route(*route_args, **kwargs)

    return wrapper


@bottle.get("/api/internal/report", authentication_required=False)
@bottle.get("/api/internal/report/", authentication_required=False)
@bottle.get("/api/internal/report/<report_uuid>", authentication_required=False)
def get_report(database: Database, report_uuid: ReportId | None = None):
    """Return the quality report, including information about other reports needed for move/copy actions."""
    date_time = report_date_time()
    data_model = latest_datamodel(database, date_time)
    reports = latest_reports_before_timestamp(database, data_model, date_time)
    summarized_reports = []
    metrics_dict = {metric_uuid: metric for report in reports for metric_uuid, metric in report.metrics_dict.items()}
    measurements = recent_measurements(database, metrics_dict, date_time)
    for report in reports:
        if not report_uuid or report["report_uuid"] == report_uuid:
            summarized_reports.append(report.summarize(measurements))
        else:
            summarized_reports.append(report)
    hide_credentials(data_model, *summarized_reports)
    return {"ok": True, "reports": summarized_reports}


@bottle.get("/api/v3/report/<report_uuid>/metric_status_summary", authentication_required=False)
@with_report
def get_report_metric_status_summary(database: Database, report: Report, report_uuid: ReportId):
    """Return a metric status summary of the report."""
    measurements = recent_measurements(database, report.metrics_dict)
    summarized_report = report.summarize(measurements)
    return {"report_uuid": report_uuid, "title": summarized_report["title"], **summarized_report["summary"]}


@bottle.post("/api/v3/report/import", permissions_required=[EDIT_REPORT_PERMISSION])
def post_report_import(database: Database):
    """Import a preconfigured report into the database."""
    report = dict(bottle.request.json)
    report["delta"] = {"uuids": [report["report_uuid"]]}

    secret = database.secrets.find_one({"name": EXPORT_FIELDS_KEYS_NAME}, {"private_key": True, "_id": False})
    if not secret:  # pragma: no feature-test-cover
        bottle.response.status = HTTPStatus.INTERNAL_SERVER_ERROR
        return {"ok": False, "error": "Cannot find the private key of this Quality-time instance."}

    private_key = secret["private_key"]
    try:
        decrypt_credentials(private_key, report)
    except DecryptionError:
        bottle.response.status = HTTPStatus.BAD_REQUEST
        return {
            "ok": False,
            "error": "Decryption of source credentials failed. \
                Did you use the public key of this Quality-time instance to encrypt this report?",
        }

    replace_report_uuids(report)
    result = insert_new_report(database, "{user} imported a new report", [report["report_uuid"]], report)
    result["new_report_uuid"] = report["report_uuid"]
    return result


@bottle.post("/api/internal/report/new", permissions_required=[EDIT_REPORT_PERMISSION])
def post_report_new(database: Database):
    """Add a new report."""
    report_uuid = uuid()
    delta_description = "{user} created a new report."
    report = {"report_uuid": report_uuid, **default_report_attributes()}
    result = insert_new_report(database, delta_description, [report_uuid], report)
    result["new_report_uuid"] = report_uuid
    return result


@bottle.post("/api/internal/report/<report_uuid>/copy", permissions_required=[EDIT_REPORT_PERMISSION])
@with_report
def post_report_copy(database: Database, report: Report, report_uuid: ReportId):
    """Copy a report."""
    report_copy = copy_report(report)
    delta_description = f"{{user}} copied the report '{report.name}'."
    uuids = [report_uuid, report_copy["report_uuid"]]
    result = insert_new_report(database, delta_description, uuids, report_copy)
    result["new_report_uuid"] = report_copy["report_uuid"]
    return result


@bottle.get("/api/internal/report/<report_uuid>/pdf", authentication_required=False)
@bottle.get("/api/v3/report/<report_uuid>/pdf", authentication_required=False)
def export_report_as_pdf(report_uuid: ReportId):
    """Download the report as PDF."""
    return export_as_pdf(report_uuid)


@bottle.get("/api/v3/report/<report_uuid>/json", authentication_required=True)
@with_report(pass_report_uuid=False)
def export_report_as_json(database: Database, report: Report):
    """Return the quality-time report, including encrypted credentials for api access to the sources."""
    if "public_key" in bottle.request.query:
        public_key = bottle.request.query["public_key"]
    else:  # default to own public key
        document = database.secrets.find_one({"name": EXPORT_FIELDS_KEYS_NAME}, {"public_key": True, "_id": False})
        if not document:  # pragma: no feature-test-cover
            bottle.response.status = HTTPStatus.INTERNAL_SERVER_ERROR
            return {"ok": False, "error": "Cannot find the public key of this Quality-time instance."}
        public_key = document["public_key"]

    encrypt_credentials(public_key, report)
    return report


@bottle.delete("/api/internal/report/<report_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
@with_report
def delete_report(database: Database, report: Report, report_uuid: ReportId):
    """Delete a report."""
    report["deleted"] = "true"
    delta_description = f"{{user}} deleted the report '{report.name}'."
    return insert_new_report(database, delta_description, [report_uuid], report)


@bottle.post(
    "/api/internal/report/<report_uuid>/attribute/<report_attribute>", permissions_required=[EDIT_REPORT_PERMISSION]
)
@with_report
def post_report_attribute(database: Database, report: Report, report_uuid: ReportId, report_attribute: str):
    """Set a report attribute."""
    new_value = dict(bottle.request.json)[report_attribute]
    if report_attribute == "comment" and new_value:
        new_value = sanitize_html(new_value)
    old_value = report.get(report_attribute) or ""
    value_change_description = "" if report_attribute == "layout" else f" from '{old_value}' to '{new_value}'"
    delta_description = f"{{user}} changed the {report_attribute} of report '{report.name}'{value_change_description}."
    report[report_attribute] = new_value
    return insert_new_report(database, delta_description, [report_uuid], report)


@bottle.post(
    "/api/internal/report/<report_uuid>/issue_tracker/<tracker_attribute>",
    permissions_required=[EDIT_REPORT_PERMISSION],
)
@with_report
def post_report_issue_tracker_attribute(
    database: Database,
    report: Report,
    report_uuid: ReportId,
    tracker_attribute: str,
):
    """Set the issue tracker attribute."""
    new_value = dict(bottle.request.json)[tracker_attribute]
    if tracker_attribute == "type":
        old_value = report.get("issue_tracker", {}).get("type") or ""
    else:
        old_value = report.get("issue_tracker", {}).get("parameters", {}).get(tracker_attribute) or ""
    if old_value == new_value:
        return {"ok": True}  # Nothing to do
    if tracker_attribute == "type":
        report.setdefault("issue_tracker", {})["type"] = new_value
    else:
        report.setdefault("issue_tracker", {}).setdefault("parameters", {})[tracker_attribute] = new_value
    if tracker_attribute in ("password", "private_token"):
        new_value, old_value = "*" * len(new_value), "*" * len(old_value)
    delta_description = (
        f"{{user}} changed the {tracker_attribute} of the issue tracker of report '{report.name}' "
        f"from '{old_value}' to '{new_value}'."
    )
    result = insert_new_report(database, delta_description, [report_uuid], report)
    issue_tracker = report.get("issue_tracker", {})
    parameters = issue_tracker.get("parameters", {})
    url_parameters = ("type", "url", "username", "password", "private_token")
    if issue_tracker.get("type") and (url := parameters.get("url")) and tracker_attribute in url_parameters:
        private_token = cast(PrivateToken, DATA_MODEL.sources[issue_tracker["type"]].parameters.get("private_token"))
        token_validation_path = private_token.validation_path if private_token else ""
        result["availability"] = [check_url_availability(url, parameters, token_validation_path)]
    return result


@bottle.get("/api/internal/report/<report_uuid>/issue_tracker/suggestions/<query>", authentication_required=True)
@with_report(pass_report_uuid=False)
def get_report_issue_tracker_suggestions(database: Database, report: Report, query: str):  # noqa: ARG001
    """Get suggestions for issue ids from the issue tracker using the query string."""
    issue_tracker = report.issue_tracker()
    # Sanitize the query. Not really needed for JQL, but can't hurt
    query = "".join(char for char in query if char.isalnum() or char.isspace())
    return {"ok": True, "suggestions": [issue.as_dict() for issue in issue_tracker.get_suggestions(query)]}


@bottle.get("/api/internal/report/<report_uuid>/issue_tracker/options", authentication_required=False)
@with_report(pass_report_uuid=False)
def get_report_issue_tracker_options(database: Database, report: Report):  # noqa: ARG001
    """Get options for the issue tracker attributes such as project key and issue type."""
    issue_tracker = report.issue_tracker()
    return issue_tracker.get_options().as_dict() | {"ok": True}


@bottle.delete("/api/internal/report/<report_uuid>/tag/<tag>", permissions_required=[EDIT_REPORT_PERMISSION])
@with_report(pass_report_uuid=False)
def delete_tag(database: Database, report: Report, tag: str):
    """Delete a tag from all metrics in a report."""
    if changed_uuids := report.delete_tag(tag):
        delta_description = f"{{user}} deleted tag '{tag}' from all metrics in report '{report.name}'."
        return insert_new_report(database, delta_description, changed_uuids, report)
    return {"ok": False, "error": f"Cannot find tag '{tag}' in report '{report.name}'."}


@bottle.post("/api/internal/report/<report_uuid>/tag/<tag>", permissions_required=[EDIT_REPORT_PERMISSION])
@with_report(pass_report_uuid=False)
def rename_tag(database: Database, report: Report, tag: str):
    """Rename a tag for all metrics in a report."""
    new_value = dict(bottle.request.json)["tag"]
    if changed_uuids := report.rename_tag(tag, new_value):
        delta_description = f"{{user}} renamed tag '{tag}' to '{new_value}' for all metrics in report '{report.name}'."
        return insert_new_report(database, delta_description, changed_uuids, report)
    return {"ok": False, "error": f"Cannot find tag '{tag}' in report '{report.name}'."}
