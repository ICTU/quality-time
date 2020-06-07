"""Subject routes."""

import bottle
from pymongo.database import Database

from database import sessions
from database.datamodels import default_subject_attributes
from database.reports import insert_new_report, ReportData, SubjectData
from model.actions import copy_subject, move_item
from server_utilities.functions import uuid
from server_utilities.type import ReportId, SubjectId


@bottle.post("/api/v2/subject/new/<report_uuid>")
def post_new_subject(report_uuid: ReportId, database: Database):
    """Create a new subject."""
    data = ReportData(database, report_uuid)
    data.report["subjects"][(subject_uuid := uuid())] = default_subject_attributes(database)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[report_uuid, subject_uuid], email=user["email"],
        description=f"{user['user']} created a new subject in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v2/subject/<subject_uuid>/copy/<report_uuid>")
def post_subject_copy(subject_uuid: SubjectId, report_uuid: ReportId, database: Database):
    """Copy a subject to a report."""
    source = SubjectData(database, subject_uuid)
    target = ReportData(database, report_uuid)
    target.report["subjects"][(subject_copy_uuid := uuid())] = copy_subject(source.subject, source.datamodel)
    user = sessions.user(database)
    delta_description = f"{user['user']} copied the subject '{source.subject_name}' from report " \
                        f"'{source.report_name}' to report '{target.report_name}'."
    target.report["delta"] = dict(
        uuids=[target.report_uuid, subject_copy_uuid], email=user["email"], description=delta_description)
    return insert_new_report(database, target.report)


@bottle.post("/api/v2/subject/<subject_uuid>/move/<target_report_uuid>")
def post_move_subject(subject_uuid: SubjectId, target_report_uuid: ReportId, database: Database):
    """Move the subject to another report."""
    source = SubjectData(database, subject_uuid)
    target = ReportData(database, target_report_uuid)
    target.report["subjects"][subject_uuid] = source.subject
    del source.report["subjects"][subject_uuid]
    user = sessions.user(database)
    delta_description = f"{user['user']} moved the subject '{source.subject_name}' from report " \
                        f"'{source.report_name}' to report '{target.report_name}'."
    source.report["delta"] = dict(
        uuids=[source.report_uuid, subject_uuid], email=user["email"], description=delta_description)
    target.report["delta"] = dict(
        uuids=[target_report_uuid, subject_uuid], email=user["email"], description=delta_description)
    return insert_new_report(database, source.report, target.report)


@bottle.delete("/api/v2/subject/<subject_uuid>")
def delete_subject(subject_uuid: SubjectId, database: Database):
    """Delete the subject."""
    data = SubjectData(database, subject_uuid)
    del data.report["subjects"][subject_uuid]
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, subject_uuid], email=user["email"],
        description=f"{user['user']} deleted the subject '{data.subject_name}' from report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v2/subject/<subject_uuid>/attribute/<subject_attribute>")
def post_subject_attribute(subject_uuid: SubjectId, subject_attribute: str, database: Database):
    """Set the subject attribute."""
    value = dict(bottle.request.json)[subject_attribute]
    data = SubjectData(database, subject_uuid)
    old_value = data.subject.get(subject_attribute) or ""
    if subject_attribute == "position":
        old_value, value = move_item(data, value, "subject")
    else:
        data.subject[subject_attribute] = value
    if old_value == value:
        return dict(ok=True)  # Nothing to do
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, subject_uuid], email=user["email"],
        description=f"{user['user']} changed the {subject_attribute} of subject "
                    f"'{data.subject_name}' in report '{data.report_name}' from '{old_value}' to '{value}'.")
    return insert_new_report(database, data.report)
