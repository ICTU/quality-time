"""Report routes."""

import bottle
import requests
from pymongo.database import Database

from database import sessions
from database.reports import copy_report, get_data, latest_reports, insert_new_report, summarize_report
from initialization.report import import_json_report
from server_utilities.functions import report_date_time, uuid
from server_utilities.type import ReportId


@bottle.post("/api/v1/report/import")
def post_report_import(database: Database):
    """Import a preconfigured report into the database."""
    report = dict(bottle.request.json)
    return import_json_report(database, report)


@bottle.post("/api/v1/report/new")
def post_report_new(database: Database):
    """Add a new report."""
    report_uuid = uuid()
    report = dict(
        report_uuid=report_uuid, title="New report", subjects={},
        delta=dict(report_uuid=report_uuid, description=f"{sessions.user(database)} created a new report."))
    return insert_new_report(database, report)


@bottle.post("/api/v1/report/<report_uuid>/copy")
def post_report_copy(report_uuid: ReportId, database: Database):
    """Copy a report."""
    data = get_data(database, report_uuid)
    report_copy = copy_report(data.report, report_copy_uuid := uuid())
    report_copy["delta"] = dict(
        report_uuid=report_copy_uuid, description=f"{sessions.user(database)} copied the report '{data.report_name}'.")
    return insert_new_report(database, report_copy)


@bottle.get("/api/v1/report/<report_uuid>/pdf")
def export_report_as_pdf(report_uuid: ReportId):
    """Download the report as pdf."""
    response = requests.get(f"http://renderer:3000/pdf?accessKey=qt&url=http://www/{report_uuid}&delay=5")
    response.raise_for_status()
    bottle.response.content_type = "application/pdf"
    return response.content


@bottle.delete("/api/v1/report/<report_uuid>")
def delete_report(report_uuid: ReportId, database: Database):
    """Delete a report."""
    data = get_data(database, report_uuid)
    data.report["deleted"] = "true"
    data.report["delta"] = dict(
        report_uuid=report_uuid, description=f"{sessions.user(database)} deleted the report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/<report_attribute>")
def post_report_attribute(report_uuid: ReportId, report_attribute: str, database: Database):
    """Set a report attribute."""
    data = get_data(database, report_uuid)
    value = dict(bottle.request.json)[report_attribute]
    old_value = data.report.get(report_attribute) or ""
    data.report[report_attribute] = value
    value_change_description = "" if report_attribute == "layout" else f" from '{old_value}' to '{value}'"
    data.report["delta"] = dict(
        report_uuid=report_uuid,
        description=f"{sessions.user(database)} changed the {report_attribute} of report '{data.report_name}'"
                    f"{value_change_description}.")
    return insert_new_report(database, data.report)


@bottle.get("/api/v1/tagreport/<tag>")
def get_tag_report(tag: str, database: Database):
    """Get a report with all metrics that have the specified tag."""
    date_time = report_date_time()
    reports = latest_reports(database, date_time)
    subjects = _get_subjects_and_metrics_by_tag(reports, tag)
    tag_report = dict(
        title=f'Report for tag "{tag}"', subtitle="Note: tag reports are read-only", report_uuid=f"tag-{tag}",
        timestamp=date_time, subjects=subjects)
    summarize_report(database, tag_report)
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
