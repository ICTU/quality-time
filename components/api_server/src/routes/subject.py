"""Subject routes."""

from typing import cast

import bottle
from pymongo.database import Database

from shared.model.subject import Subject
from shared.utils.type import ReportId, SubjectId

from database.datamodels import default_subject_attributes, latest_datamodel
from database.reports import insert_new_report, latest_report_for_uuids, latest_reports
from model.actions import copy_subject, move_item
from utils.functions import sanitize_html, uuid

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION


@bottle.post("/api/v3/subject/new/<report_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_new_subject(report_uuid: ReportId, database: Database):
    """Create a new subject."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    report = latest_report_for_uuids(reports, report_uuid)[0]
    subject_type = str(dict(bottle.request.json)["type"])
    subject_uuid = cast(SubjectId, uuid())
    report.subjects_dict[subject_uuid] = cast(Subject, default_subject_attributes(database, subject_type))
    delta_description = f"{{user}} created a new subject in report '{report.name}'."
    uuids = [report_uuid, subject_uuid]
    result = insert_new_report(database, delta_description, uuids, report)
    result["new_subject_uuid"] = subject_uuid
    return result


@bottle.post("/api/v3/subject/<subject_uuid>/copy/<report_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_subject_copy(subject_uuid: SubjectId, report_uuid: ReportId, database: Database):
    """Add a copy of the subject to the report (new in v3)."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    source_and_target_reports = latest_report_for_uuids(reports, subject_uuid, report_uuid)
    source_report = source_and_target_reports[0]
    target_report = source_and_target_reports[1]
    subject = source_report.subjects_dict[subject_uuid]
    subject_copy_uuid = cast(SubjectId, uuid())
    target_report.subjects_dict[subject_copy_uuid] = copy_subject(subject, data_model)
    delta_description = (
        f"{{user}} copied the subject '{subject.name}' from report "
        f"'{source_report.name}' to report '{target_report.name}'."
    )
    uuids = [target_report.uuid, subject_copy_uuid]
    result = insert_new_report(database, delta_description, uuids, target_report)
    result["new_subject_uuid"] = subject_copy_uuid
    return result


@bottle.post("/api/v3/subject/<subject_uuid>/move/<target_report_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_move_subject(subject_uuid: SubjectId, target_report_uuid: ReportId, database: Database):
    """Move the subject to another report."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    source_and_target_reports = latest_report_for_uuids(reports, subject_uuid, target_report_uuid)
    source_report = source_and_target_reports[0]
    target_report = source_and_target_reports[1]
    subject = source_report.subjects_dict[subject_uuid]
    target_report.subjects_dict[subject_uuid] = subject
    del source_report.subjects_dict[subject_uuid]
    delta_description = (
        f"{{user}} moved the subject '{subject.name}' from report "
        f"'{source_report.name}' to report '{target_report.name}'."
    )
    uuids = [target_report_uuid, source_report.uuid, subject_uuid]
    return insert_new_report(database, delta_description, uuids, source_report, target_report)


@bottle.delete("/api/v3/subject/<subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def delete_subject(subject_uuid: SubjectId, database: Database):
    """Delete the subject."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    report = latest_report_for_uuids(reports, subject_uuid)[0]
    subject = report.subjects_dict[subject_uuid]
    del report["subjects"][subject_uuid]
    delta_description = f"{{user}} deleted the subject '{subject.name}' from report '{report.name}'."
    uuids = [report.uuid, subject_uuid]
    return insert_new_report(database, delta_description, uuids, report)


@bottle.post(
    "/api/v3/subject/<subject_uuid>/attribute/<subject_attribute>",
    permissions_required=[EDIT_REPORT_PERMISSION],
)
def post_subject_attribute(subject_uuid: SubjectId, subject_attribute: str, database: Database):
    """Set the subject attribute."""
    new_value = dict(bottle.request.json)[subject_attribute]
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    report = latest_report_for_uuids(reports, subject_uuid)[0]
    subject = report.subjects_dict[subject_uuid]
    old_subject_name = subject.name  # In case the name is the attribute that is changed
    if subject_attribute == "comment" and new_value:
        new_value = sanitize_html(new_value)
    old_value = subject.get(subject_attribute) or ""
    if subject_attribute == "position":
        old_value, new_value = move_item(report, subject, new_value)
    else:
        subject[subject_attribute] = new_value
    if old_value == new_value:
        return {"ok": True}  # Nothing to do
    delta_description = (
        f"{{user}} changed the {subject_attribute} of subject "
        f"'{old_subject_name}' in report '{report.name}' from '{old_value}' to '{new_value}'."
    )
    uuids = [report.uuid, subject.uuid]
    return insert_new_report(database, delta_description, uuids, report)
