"""Report routes."""

import os

import bottle
import requests
from pymongo.database import Database

from database import sessions
from database.datamodels import latest_datamodel
from database.measurements import last_measurements
from database.reports import get_data, latest_summarized_reports, insert_new_report, summarize_report
from model.actions import copy_report
from model.transformations import hide_credentials
from initialization.report import import_json_report
from server_utilities.functions import report_date_time, uuid
from server_utilities.type import ReportId


@bottle.post("/api/v1/report/import")
@bottle.post("/api/v2/report/import")
def post_report_import(database: Database):
    """Import a preconfigured report into the database."""
    report = dict(bottle.request.json)
    return import_json_report(database, report)


@bottle.post("/api/v1/report/new")
@bottle.post("/api/v2/report/new")
def post_report_new(database: Database):
    """Add a new report."""
    report_uuid = uuid()
    user = sessions.user(database)
    report = dict(
        report_uuid=report_uuid, title="New report", subjects={},
        delta=dict(uuids=[report_uuid], email=user["email"], description=f"{user['user']} created a new report."))
    return insert_new_report(database, report)


@bottle.post("/api/v1/report/<report_uuid>/copy")
@bottle.post("/api/v2/report/<report_uuid>/copy")
def post_report_copy(report_uuid: ReportId, database: Database):
    """Copy a report."""
    data = get_data(database, report_uuid)
    report_copy = copy_report(data.report, data.datamodel)
    user = sessions.user(database)
    report_copy["delta"] = dict(
        uuids=[report_uuid, report_copy["report_uuid"]], email=user["email"],
        description=f"{user['user']} copied the report '{data.report_name}'.")
    return insert_new_report(database, report_copy)


@bottle.get("/api/v1/report/<report_uuid>/pdf")
@bottle.get("/api/v2/report/<report_uuid>/pdf")
def export_report_as_pdf(report_uuid: ReportId):
    """Download the report as pdf."""
    host = os.environ.get("PROXY_HOST", "www")
    port = os.environ.get("PROXY_PORT", "80")
    margins = "&".join([f"pdf.margin.{side}=25" for side in ("top", "bottom", "left", "right")])
    # Set pdf scale to 70% or otherwise the dashboard falls off the page
    options = f"emulateScreenMedia=false&goto.timeout=60000&pdf.scale=0.7&{margins}"
    response = requests.get(f"http://renderer:3000/pdf?accessKey=qt&url=http://{host}:{port}/{report_uuid}&{options}")
    response.raise_for_status()
    bottle.response.content_type = "application/pdf"
    return response.content


@bottle.delete("/api/v1/report/<report_uuid>")
@bottle.delete("/api/v2/report/<report_uuid>")
def delete_report(report_uuid: ReportId, database: Database):
    """Delete a report."""
    data = get_data(database, report_uuid)
    data.report["deleted"] = "true"
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[report_uuid], email=user["email"],
        description=f"{user['user']} deleted the report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/<report_attribute>")
@bottle.post("/api/v2/report/<report_uuid>/attribute/<report_attribute>")
def post_report_attribute(report_uuid: ReportId, report_attribute: str, database: Database):
    """Set a report attribute."""
    data = get_data(database, report_uuid)
    value = dict(bottle.request.json)[report_attribute]
    old_value = data.report.get(report_attribute) or ""
    data.report[report_attribute] = value
    value_change_description = "" if report_attribute == "layout" else f" from '{old_value}' to '{value}'"
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[report_uuid], email=user["email"],
        description=f"{user['user']} changed the {report_attribute} of report '{data.report_name}'"
                    f"{value_change_description}.")
    return insert_new_report(database, data.report)


@bottle.get("/api/v1/tagreport/<tag>")
@bottle.get("/api/v2/tagreport/<tag>")
def get_tag_report(tag: str, database: Database):
    """Get a report with all metrics that have the specified tag."""
    date_time = report_date_time()
    data_model = latest_datamodel(database)
    reports = latest_summarized_reports(database, data_model, date_time)
    hide_credentials(data_model, *reports)
    subjects = _get_subjects_and_metrics_by_tag(reports, tag)
    tag_report = dict(
        title=f'Report for tag "{tag}"', subtitle="Note: tag reports are read-only", report_uuid=f"tag-{tag}",
        timestamp=date_time, subjects=subjects)
    last_measurements_by_metric_uuid = {m["metric_uuid"]: m for m in last_measurements(database)}
    summarize_report(tag_report, last_measurements_by_metric_uuid, data_model)
    return tag_report


def _get_subjects_and_metrics_by_tag(reports, tag: str):
    """Return all subjects and metrics that have the tag."""
    subjects = dict()
    for report in reports:
        for subject_uuid, subject in list(report.get("subjects", {}).items()):
            for metric_uuid, metric in list(subject.get("metrics", {}).items()):
                if tag not in metric.get("tags", []):
                    del subject["metrics"][metric_uuid]
            if subject.get("metrics", {}):
                subject["name"] = report["title"] + " / " + subject["name"]
                subjects[subject_uuid] = subject
    return subjects
