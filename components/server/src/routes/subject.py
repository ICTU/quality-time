"""Subject routes."""

import bottle
from pymongo.database import Database

from database import sessions
from database.datamodels import default_subject_attributes
from database.reports import get_data, insert_new_report
from model.actions import copy_subject, move_item
from server_utilities.functions import uuid
from server_utilities.type import ReportId, SubjectId


@bottle.post("/api/v1/report/<report_uuid>/subject/new")
def post_new_subject(report_uuid: ReportId, database: Database):
    """Create a new subject."""
    data = get_data(database, report_uuid)
    data.report["subjects"][uuid()] = default_subject_attributes(database)
    data.report["delta"] = dict(
        report_uuid=report_uuid,
        description=f"{sessions.user(database)} created a new subject in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/subject/<subject_uuid>/copy")
def post_subject_copy(report_uuid: ReportId, subject_uuid: SubjectId, database: Database):
    """Copy a subject."""
    data = get_data(database, report_uuid, subject_uuid=subject_uuid)
    data.report["subjects"][uuid()] = copy_subject(data.subject, data.datamodel)
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid,
        description=f"{sessions.user(database)} copied the subject '{data.subject_name}' in report "
                    f"'{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.delete("/api/v1/report/<report_uuid>/subject/<subject_uuid>")
def delete_subject(report_uuid: ReportId, subject_uuid: SubjectId, database: Database):
    """Delete the subject."""
    data = get_data(database, report_uuid, subject_uuid)
    del data.report["subjects"][subject_uuid]
    data.report["delta"] = dict(
        report_uuid=report_uuid,
        description=f"{sessions.user(database)} deleted the subject '{data.subject_name}' from report "
                    f"'{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/subject/<subject_uuid>/<subject_attribute>")
def post_subject_attribute(report_uuid: ReportId, subject_uuid: SubjectId, subject_attribute: str, database: Database):
    """Set the subject attribute."""
    value = dict(bottle.request.json)[subject_attribute]
    data = get_data(database, report_uuid, subject_uuid)
    old_value = data.subject.get(subject_attribute) or ""
    if subject_attribute == "position":
        old_value, value = move_item(data, value, "subject")
    else:
        data.subject[subject_attribute] = value
    if old_value == value:
        return dict(ok=True)  # Nothing to do
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=subject_uuid,
        description=f"{sessions.user(database)} changed the {subject_attribute} of subject '{data.subject_name}' in "
                    f"report '{data.report_name}' from '{old_value}' to '{value}'.")
    return insert_new_report(database, data.report)
