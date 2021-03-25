"""Subject routes."""

from datetime import datetime, timedelta
import bottle
from pymongo.database import Database

from database.datamodels import default_subject_attributes, latest_datamodel
from database.measurements import measurements_by_metric
from database.reports import insert_new_report, latest_reports, metrics_of_subject
from model.actions import copy_subject, move_item
from model.data import ReportData, SubjectData
from routes.plugins.auth_plugin import EDIT_REPORT_PERMISSION
from server_utilities.functions import report_date_time, uuid
from server_utilities.type import MetricId, ReportId, SubjectId


@bottle.post("/api/v3/subject/new/<report_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_new_subject(report_uuid: ReportId, database: Database):
    """Create a new subject."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = ReportData(data_model, reports, report_uuid)
    data.report["subjects"][(subject_uuid := uuid())] = default_subject_attributes(database)
    delta_description = f"{{user}} created a new subject in report '{data.report_name}'."
    uuids = [report_uuid, subject_uuid]
    result = insert_new_report(database, delta_description, (data.report, uuids))
    result["new_subject_uuid"] = subject_uuid
    return result


@bottle.post("/api/v3/subject/<subject_uuid>/copy/<report_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_subject_copy(subject_uuid: SubjectId, report_uuid: ReportId, database: Database):
    """Add a copy of the subject to the report (new in v3)."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    source = SubjectData(data_model, reports, subject_uuid)
    target = ReportData(data_model, reports, report_uuid)
    target.report["subjects"][(subject_copy_uuid := uuid())] = copy_subject(source.subject, source.datamodel)
    delta_description = (
        f"{{user}} copied the subject '{source.subject_name}' from report "
        f"'{source.report_name}' to report '{target.report_name}'."
    )
    uuids = [target.report_uuid, subject_copy_uuid]
    result = insert_new_report(database, delta_description, (target.report, uuids))
    result["new_subject_uuid"] = subject_copy_uuid
    return result


@bottle.post("/api/v3/subject/<subject_uuid>/move/<target_report_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
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
    source_uuids = [source.report_uuid, subject_uuid]
    target_uuids = [target_report_uuid, subject_uuid]
    return insert_new_report(database, delta_description, (source.report, source_uuids), (target.report, target_uuids))


@bottle.delete("/api/v3/subject/<subject_uuid>", permissions_required=[EDIT_REPORT_PERMISSION])
def delete_subject(subject_uuid: SubjectId, database: Database):
    """Delete the subject."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = SubjectData(data_model, reports, subject_uuid)
    del data.report["subjects"][subject_uuid]
    delta_description = f"{{user}} deleted the subject '{data.subject_name}' from report '{data.report_name}'."
    uuids = [data.report_uuid, subject_uuid]
    return insert_new_report(database, delta_description, (data.report, uuids))


@bottle.post(
    "/api/v3/subject/<subject_uuid>/attribute/<subject_attribute>", permissions_required=[EDIT_REPORT_PERMISSION]
)
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
    delta_description = (
        f"{{user}} changed the {subject_attribute} of subject "
        f"'{data.subject_name}' in report '{data.report_name}' from '{old_value}' to '{value}'."
    )
    uuids = [data.report_uuid, subject_uuid]
    return insert_new_report(database, delta_description, (data.report, uuids))


@bottle.get("/api/v3/subject/<subject_uuid>/measurements", authentication_required=False)
def get_subject_measurements(subject_uuid: SubjectId, database: Database):
    """Return all measurements for the subjects within the last 28 weeks."""
    metric_uuids: list[MetricId] = metrics_of_subject(database, subject_uuid)

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
