"""Subject routes."""

from typing import List
from datetime import datetime, timedelta
import bottle
from pymongo.database import Database

from database.datamodels import default_subject_attributes, latest_datamodel
from database.measurements import measurements_by_metric
from database.reports import insert_new_report, latest_reports, metrics_of_subject
from model.actions import copy_subject, move_item
from model.data import ReportData, SubjectData
from server_utilities.functions import report_date_time, uuid
from server_utilities.type import MetricId, ReportId, SubjectId


@bottle.post("/api/v3/subject/new/<report_uuid>")
def post_new_subject(report_uuid: ReportId, database: Database):
    """Create a new subject."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = ReportData(data_model, reports, report_uuid)
    data.report["subjects"][(subject_uuid := uuid())] = default_subject_attributes(database)
    data.report["delta"] = dict(
        uuids=[report_uuid, subject_uuid],
        email=user["email"],
        description=f"{{user}} created a new subject in report '{data.report_name}'.",
    )
    result = insert_new_report(database, data.report)
    result["new_subject_uuid"] = subject_uuid
    return result


@bottle.post("/api/v3/subject/<subject_uuid>/copy/<report_uuid>")
def post_subject_copy(subject_uuid: SubjectId, report_uuid: ReportId, database: Database):
    """Add a copy of the subject to the report (new in v3)."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    source = SubjectData(data_model, reports, subject_uuid)
    target = ReportData(data_model, reports, report_uuid)
    target.report["subjects"][(subject_copy_uuid := uuid())] = copy_subject(source.subject, source.datamodel)
    target.report["delta"] = dict(
        uuids=[target.report_uuid, subject_copy_uuid],
        email=user["email"],
        description=f"{{user}} copied the subject '{source.subject_name}' from report "
        f"'{source.report_name}' to report '{target.report_name}'.",
    )
    result = insert_new_report(database, target.report)
    result["new_subject_uuid"] = subject_copy_uuid
    return result


@bottle.post("/api/v3/subject/<subject_uuid>/move/<target_report_uuid>")
def post_move_subject(subject_uuid: SubjectId, target_report_uuid: ReportId, database: Database):
    """Move the subject to another report."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    source = SubjectData(data_model, reports, subject_uuid)
    target = ReportData(data_model, reports, target_report_uuid)
    target.report["subjects"][subject_uuid] = source.subject
    del source.report["subjects"][subject_uuid]
    delta_description = (
        f"{{user}} moved the subject '{source.subject_name}' from report "
        f"'{source.report_name}' to report '{target.report_name}'."
    )
    source.report["delta"] = dict(uuids=[source.report_uuid, subject_uuid], description=delta_description)
    target.report["delta"] = dict(uuids=[target_report_uuid, subject_uuid], description=delta_description)
    return insert_new_report(database, source.report, target.report)


@bottle.delete("/api/v3/subject/<subject_uuid>")
def delete_subject(subject_uuid: SubjectId, database: Database):
    """Delete the subject."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = SubjectData(data_model, reports, subject_uuid)
    del data.report["subjects"][subject_uuid]
    data.report["delta"] = dict(
        uuids=[data.report_uuid, subject_uuid],
        email=user["email"],
        description=f"{{user}} deleted the subject '{data.subject_name}' from report '{data.report_name}'.",
    )
    return insert_new_report(database, data.report)


@bottle.post("/api/v3/subject/<subject_uuid>/attribute/<subject_attribute>")
def post_subject_attribute(subject_uuid: SubjectId, subject_attribute: str, database: Database):
    """Set the subject attribute."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = SubjectData(data_model, reports, subject_uuid)
    value = dict(bottle.request.json)[subject_attribute]
    old_value = data.subject.get(subject_attribute) or ""
    if subject_attribute == "position":
        old_value, value = move_item(data, value, "subject")
    else:
        data.subject[subject_attribute] = value
    if old_value == value:
        return dict(ok=True)  # Nothing to do
    data.report["delta"] = dict(
        uuids=[data.report_uuid, subject_uuid],
        description=f"{{user}} changed the {subject_attribute} of subject "
        f"'{data.subject_name}' in report '{data.report_name}' from '{old_value}' to '{value}'.",
    )
    return insert_new_report(database, data.report)


@bottle.get("/api/v3/subject/<subject_uuid>/measurements")
def get_subject_measurements(subject_uuid: SubjectId, database: Database):
    """Return all measurements for the subjects within the last 28 weeks."""
    metric_uuids: List[MetricId] = metrics_of_subject(database, subject_uuid)

    report_timestamp = datetime.fromisoformat(report_date_time()) if report_date_time() != "" else datetime.now()
    min_datetime = report_timestamp - timedelta(weeks=28)
    min_iso_timestamp = min_datetime.isoformat()

    return dict(
        measurements=list(
            measurements_by_metric(
                database, *metric_uuids, min_iso_timestamp=min_iso_timestamp, max_iso_timestamp=report_date_time()
            )
        )
    )
