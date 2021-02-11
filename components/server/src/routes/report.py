"""Report routes."""

import os
from urllib import parse

import bottle
import requests
from pymongo.database import Database

from database.datamodels import latest_datamodel
from database.measurements import recent_measurements_by_metric_uuid
from database.reports import insert_new_report, latest_report, latest_reports
from initialization.report import import_json_report
from initialization.secrets import EXPORT_FIELDS_KEYS_NAME
from model.actions import copy_report
from model.data import ReportData
from model.transformations import encrypt_credentials, hide_credentials, summarize_report
from server_utilities.functions import iso_timestamp, report_date_time, uuid
from server_utilities.type import ReportId


@bottle.get("/api/v3/report/<report_uuid>")
def get_report(database: Database, report_uuid: ReportId):
    """Return the quality report, including information about other reports needed for move/copy actions."""
    date_time = report_date_time()
    data_model = latest_datamodel(database, date_time)
    reports = latest_reports(database, date_time)
    for report in reports:
        if report["report_uuid"] == report_uuid:
            recent_measurements = recent_measurements_by_metric_uuid(database, date_time)
            summarize_report(report, recent_measurements, data_model)
            break
    hide_credentials(data_model, *reports)
    return dict(reports=reports)


@bottle.post("/api/v3/report/import")
def post_report_import(database: Database):
    """Import a preconfigured report into the database."""
    report = dict(bottle.request.json)
    report["delta"] = dict(uuids=[report["report_uuid"]])
    result = import_json_report(database, report)
    result["new_report_uuid"] = report["report_uuid"]
    return result


@bottle.post("/api/v3/report/new")
def post_report_new(database: Database):
    """Add a new report."""
    report_uuid = uuid()
    delta_description = "{user} created a new report."
    report = dict(report_uuid=report_uuid, title="New report", subjects={})
    result = insert_new_report(database, delta_description, (report, [report_uuid]))
    result["new_report_uuid"] = report_uuid
    return result


@bottle.post("/api/v3/report/<report_uuid>/copy")
def post_report_copy(report_uuid: ReportId, database: Database):
    """Copy a report."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = ReportData(data_model, reports, report_uuid)
    report_copy = copy_report(data.report, data.datamodel)
    delta_description = f"{{user}} copied the report '{data.report_name}'."
    uuids = [report_uuid, report_copy["report_uuid"]]
    result = insert_new_report(database, delta_description, (report_copy, uuids))
    result["new_report_uuid"] = report_copy["report_uuid"]
    return result


@bottle.get("/api/v3/report/<report_uuid>/pdf")
def export_report_as_pdf(report_uuid: ReportId):
    """Download the report as pdf."""
    renderer_host = os.environ.get("RENDERER_HOST", "renderer")
    renderer_port = os.environ.get("RENDERER_PORT", "9000")
    render_url = f"http://{renderer_host}:{renderer_port}/api/render"
    proxy_host = os.environ.get("PROXY_HOST", "www")
    proxy_port = os.environ.get("PROXY_PORT", "80")
    query_string = f"?{bottle.request.query_string}" if bottle.request.query_string else ""
    report_url = parse.quote(f"http://{proxy_host}:{proxy_port}/{report_uuid}{query_string}")
    margins = "&".join([f"pdf.margin.{side}=25" for side in ("top", "bottom", "left", "right")])
    # Set pdf scale to 70% or otherwise the dashboard falls off the page
    options = f"emulateScreenMedia=false&goto.timeout=60000&scrollPage=true&waitFor=10000&pdf.scale=0.7&{margins}"
    response = requests.get(f"{render_url}?url={report_url}&{options}")
    response.raise_for_status()
    bottle.response.content_type = "application/pdf"
    return response.content


@bottle.get("/api/v3/report/<report_uuid>/json")
def export_report_as_json(database: Database, report_uuid: ReportId):
    """Return the quality report, including information about other reports needed for move/copy actions."""
    date_time = report_date_time()
    data_model = latest_datamodel(database, date_time)
    report = latest_report(database, report_uuid)

    # pylint doesn't seem to be able to see that bottle.request.query is dict(like) at runtime
    if "public_key" in bottle.request.query:  # pylint: disable=unsupported-membership-test
        public_key = bottle.request.query["public_key"]  # pylint: disable=unsupported-membership-test
    else:  # default to own public key
        document = database.secrets.find_one({"name": EXPORT_FIELDS_KEYS_NAME}, {"public_key": True, "_id": False})
        if not document:
            raise Exception("Could not find keys dor encryting api credentials.")
        public_key = document["public_key"]

    encrypt_credentials(data_model, public_key, report)
    return report


@bottle.delete("/api/v3/report/<report_uuid>")
def delete_report(report_uuid: ReportId, database: Database):
    """Delete a report."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = ReportData(data_model, reports, report_uuid)
    data.report["deleted"] = "true"
    delta_description = f"{{user}} deleted the report '{data.report_name}'."
    return insert_new_report(database, delta_description, (data.report, [report_uuid]))


@bottle.post("/api/v3/report/<report_uuid>/attribute/<report_attribute>")
def post_report_attribute(report_uuid: ReportId, report_attribute: str, database: Database):
    """Set a report attribute."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = ReportData(data_model, reports, report_uuid)
    value = dict(bottle.request.json)[report_attribute]
    old_value = data.report.get(report_attribute) or ""
    data.report[report_attribute] = value
    value_change_description = "" if report_attribute == "layout" else f" from '{old_value}' to '{value}'"
    delta_description = (
        f"{{user}} changed the {report_attribute} of report '{data.report_name}'{value_change_description}."
    )
    return insert_new_report(database, delta_description, (data.report, [report_uuid]))


@bottle.get("/api/v3/tagreport/<tag>")
def get_tag_report(tag: str, database: Database):
    """Get a report with all metrics that have the specified tag."""
    date_time = report_date_time()
    reports = latest_reports(database, date_time)
    data_model = latest_datamodel(database, date_time)
    subjects = _get_subjects_and_metrics_by_tag(data_model, reports, tag)
    tag_report = dict(
        title=f'Report for tag "{tag}"',
        subtitle="Note: tag reports are read-only",
        report_uuid=f"tag-{tag}",
        timestamp=iso_timestamp(),
        subjects=subjects,
    )
    hide_credentials(data_model, tag_report)
    summarize_report(tag_report, recent_measurements_by_metric_uuid(database, date_time), data_model)
    return tag_report


def _get_subjects_and_metrics_by_tag(data_model, reports, tag: str):
    """Return all subjects and metrics that have the tag."""
    subjects = {}
    for report in reports:
        for subject_uuid, subject in list(report.get("subjects", {}).items()):
            for metric_uuid, metric in list(subject.get("metrics", {}).items()):
                if tag not in metric.get("tags", []):
                    del subject["metrics"][metric_uuid]
            if subject.get("metrics", {}):
                subject_name = subject.get("name") or data_model["subjects"][subject["type"]]["name"]
                subject["name"] = report["title"] + " / " + subject_name
                subjects[subject_uuid] = subject
    return subjects
