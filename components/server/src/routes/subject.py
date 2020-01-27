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
@bottle.post("/api/v2/subject/new/<report_uuid>")
def post_new_subject(report_uuid: ReportId, database: Database):
    """Create a new subject."""
    data = get_data(database, report_uuid)
    data.report["subjects"][(subject_uuid := uuid())] = default_subject_attributes(database)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[report_uuid, subject_uuid], email=user["email"],
        description=f"{user['user']} created a new subject in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/subject/<subject_uuid>/copy")
def post_subject_copy_v1(report_uuid: ReportId, subject_uuid: SubjectId, database: Database):
    """Copy a subject."""
    # pylint: disable=unused-argument
    return post_subject_copy(subject_uuid, database)  # pragma: nocover


@bottle.post("/api/v2/subject/<subject_uuid>/copy")
def post_subject_copy(subject_uuid: SubjectId, database: Database):
    """Copy a subject."""
    data = get_data(database, subject_uuid=subject_uuid)
    data.report["subjects"][(subject_copy_uuid := uuid())] = copy_subject(data.subject, data.datamodel)
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, subject_copy_uuid], email=user["email"],
        description=f"{user['user']} copied the subject '{data.subject_name}' in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v2/subject/<subject_uuid>/move/<target_report_uuid>")
def post_move_subject(subject_uuid: SubjectId, target_report_uuid: ReportId, database: Database):
    """Move the subject to another report."""
    source = get_data(database, subject_uuid=subject_uuid)
    target = get_data(database, report_uuid=target_report_uuid)
    target.report["subjects"][subject_uuid] = source.subject
    del source.report["subjects"][subject_uuid]
    user = sessions.user(database)
    delta_description = f"{user['user']} moved the subject '{source.subject_name}' from report " \
                        f"'{source.report_name}' to report '{target.report_name}'."
    source.report["delta"] = dict(
        uuids=[source.report_uuid, subject_uuid], email=user["email"], description=delta_description)
    target.report["delta"] = dict(
        uuids=[target_report_uuid, subject_uuid], email=user["email"], description=delta_description)
    insert_new_report(database, target.report)
    return insert_new_report(database, source.report)


@bottle.delete("/api/v1/report/<report_uuid>/subject/<subject_uuid>")
def delete_subject_v1(report_uuid: ReportId, subject_uuid: SubjectId, database: Database):
    """Delete the subject."""
    # pylint: disable=unused-argument
    return delete_subject(subject_uuid, database)  # pragma: nocover


@bottle.delete("/api/v2/subject/<subject_uuid>")
def delete_subject(subject_uuid: SubjectId, database: Database):
    """Delete the subject."""
    data = get_data(database, subject_uuid=subject_uuid)
    del data.report["subjects"][subject_uuid]
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, subject_uuid], email=user["email"],
        description=f"{user['user']} deleted the subject '{data.subject_name}' from report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.post("/api/v1/report/<report_uuid>/subject/<subject_uuid>/<subject_attribute>")
def post_subject_attribute_v1(
        report_uuid: ReportId, subject_uuid: SubjectId, subject_attribute: str, database: Database):
    """Set the subject attribute."""
    # pylint: disable=unused-argument
    return post_subject_attribute(subject_uuid, subject_attribute, database)  # pragma: nocover


@bottle.post("/api/v2/subject/<subject_uuid>/attribute/<subject_attribute>")
def post_subject_attribute(subject_uuid: SubjectId, subject_attribute: str, database: Database):
    """Set the subject attribute."""
    value = dict(bottle.request.json)[subject_attribute]
    data = get_data(database, subject_uuid=subject_uuid)
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
