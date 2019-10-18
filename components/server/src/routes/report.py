"""Report routes."""

from collections import namedtuple
from typing import Any, Dict, Tuple

from pymongo.database import Database
import bottle

from database.datamodels import (
    latest_datamodel, default_subject_attributes, default_metric_attributes, default_source_parameters
)
from database.reports import (
    latest_reports, latest_report, insert_new_report, latest_reports_overview, insert_new_reports_overview,
    summarize_report
)
from database import sessions
from utilities.functions import report_date_time, uuid, sanitize_html
from utilities.type import MetricId, ReportId, SourceId, SubjectId
from .measurement import latest_measurement, insert_new_measurement


def get_subject_uuid(report, metric_uuid: MetricId):
    """Return the uuid of the subject that has the metric with the specified uuid."""
    subjects = report["subjects"]
    return [subject_uuid for subject_uuid in subjects if metric_uuid in subjects[subject_uuid]["metrics"]][0]


def get_metric_uuid(report, source_uuid: SourceId):
    """Return the uuid of the metric that has a source with the specified uuid."""
    return [metric_uuid for subject in report["subjects"].values() for metric_uuid in subject["metrics"]
            if source_uuid in subject["metrics"][metric_uuid]["sources"]][0]


def get_data(database: Database, report_uuid: ReportId, subject_uuid: SubjectId = None, metric_uuid: MetricId = None,
             source_uuid: SourceId = None):
    """Return applicable report, subject, metric, source, and their uuids and names."""
    data = namedtuple(
        "data",
        "datamodel, report, report_name, subject, subject_uuid, subject_name, "
        "metric, metric_uuid, metric_name, source, source_uuid, source_name")
    data.report = latest_report(database, report_uuid)
    data.report_name = data.report.get("title") or ""
    data.source_uuid = source_uuid
    data.metric_uuid = get_metric_uuid(data.report, data.source_uuid) if data.source_uuid else metric_uuid
    data.subject_uuid = get_subject_uuid(data.report, data.metric_uuid) if data.metric_uuid else subject_uuid
    data.datamodel = latest_datamodel(database)
    if data.subject_uuid:
        data.subject = data.report["subjects"][data.subject_uuid]
        data.subject_name = data.subject.get("name") or data.datamodel["subjects"][data.subject["type"]]["name"]
    if data.metric_uuid:
        data.metric = data.subject["metrics"][data.metric_uuid]
        data.metric_name = data.metric.get("name") or data.datamodel["metrics"][data.metric["type"]]["name"]
    if data.source_uuid:
        data.source = data.metric["sources"][data.source_uuid]
        data.source_name = data.source.get("name") or data.datamodel["sources"][data.source["type"]]["name"]
    return data


@bottle.post("/report/<report_uuid>/<report_attribute>")
def post_report_attribute(report_uuid: ReportId, report_attribute: str, database: Database):
    """Set a report attribute."""
    data = get_data(database, report_uuid)
    value = dict(bottle.request.json)[report_attribute]
    old_value = data.report.get(report_attribute) or ""
    data.report[report_attribute] = value
    data.report["delta"] = dict(
        report_uuid=report_uuid,
        description=f"{sessions.user(database)} changed the {report_attribute} of report '{data.report_name}' from "
                    f"'{old_value}' to '{value}'.")
    return insert_new_report(database, data.report)


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/<subject_attribute>")
def post_subject_attribute(report_uuid: ReportId, subject_uuid: SubjectId, subject_attribute: str, database: Database):
    """Set the subject attribute."""
    value = dict(bottle.request.json)[subject_attribute]
    data = get_data(database, report_uuid, subject_uuid)
    old_value = data.subject.get(subject_attribute) or ""
    data.subject[subject_attribute] = value
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=subject_uuid,
        description=f"{sessions.user(database)} changed the {subject_attribute} of subject '{data.subject_name}' in "
                    f"report '{data.report_name}' from '{old_value}' to '{value}'.")
    return insert_new_report(database, data.report)


@bottle.post("/report/<report_uuid>/subject/new")
def post_new_subject(report_uuid: ReportId, database: Database):
    """Create a new subject."""
    data = get_data(database, report_uuid)
    data.report["subjects"][uuid()] = default_subject_attributes(database)
    data.report["delta"] = dict(
        report_uuid=report_uuid,
        description=f"{sessions.user(database)} created a new subject in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.delete("/report/<report_uuid>/subject/<subject_uuid>")
def delete_subject(report_uuid: ReportId, subject_uuid: SubjectId, database: Database):
    """Delete the subject."""
    data = get_data(database, report_uuid, subject_uuid)
    del data.report["subjects"][subject_uuid]
    data.report["delta"] = dict(
        report_uuid=report_uuid,
        description=f"{sessions.user(database)} deleted the subject '{data.subject_name}' from report "
                    f"'{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.get("/metrics")
def get_metrics(database: Database):
    """Get all metrics."""
    metrics: Dict[str, Any] = {}
    reports = get_reports(database)
    for report in reports["reports"]:
        for subject in report["subjects"].values():
            metrics.update(subject["metrics"])
    return metrics


@bottle.post("/report/<report_uuid>/metric/<metric_uuid>/<metric_attribute>")
def post_metric_attribute(report_uuid: ReportId, metric_uuid: MetricId, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    value = dict(bottle.request.json)[metric_attribute]
    data = get_data(database, report_uuid, metric_uuid=metric_uuid)
    old_value = data.metric.get(metric_attribute) or ""
    if metric_attribute == "comment" and value:
        value = sanitize_html(value)
    if metric_attribute == "position":
        old_value, value = move_metric(data, value)
    else:
        data.metric[metric_attribute] = value
    if old_value == value:
        return dict(ok=True)  # Nothing to do
    if metric_attribute == "type":
        data.metric.update(default_metric_attributes(database, report_uuid, value))
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid, metric_uuid=metric_uuid,
        description=f"{sessions.user(database)} changed the {metric_attribute} of metric '{data.metric_name}' of "
                    f"subject '{data.subject_name}' in report '{data.report_name}' from '{old_value}' to '{value}'.")
    insert_new_report(database, data.report)
    if metric_attribute in ("accept_debt", "debt_target", "debt_end_date", "direction", "near_target", "target"):
        if latest := latest_measurement(database, metric_uuid):
            return insert_new_measurement(database, latest, data.metric)
    return dict(ok=True)


def move_metric(data, new_position: str) -> Tuple[int, int]:
    """Change the metric position."""
    metrics = data.subject["metrics"]
    nr_metrics = len(metrics)
    old_index = list(metrics.keys()).index(data.metric_uuid)
    new_index = dict(
        first=0, last=nr_metrics - 1, previous=max(0, old_index - 1),
        next=min(nr_metrics - 1, old_index + 1))[new_position]
    # Dicts are guaranteed to be (insertion) ordered starting in Python 3.7, but there's no API to change the order so
    # we construct a new metrics dict in the right order and insert that in the report.
    reordered_metrics: Dict[str, Dict] = dict()
    del metrics[data.metric_uuid]
    for metric_uuid, metric in metrics.items():
        if len(reordered_metrics) == new_index:
            reordered_metrics[data.metric_uuid] = data.metric
        reordered_metrics[metric_uuid] = metric
    if len(reordered_metrics) == new_index:
        reordered_metrics[data.metric_uuid] = data.metric
    data.subject["metrics"] = reordered_metrics
    return old_index, new_index


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/metric/new")
def post_metric_new(report_uuid: ReportId, subject_uuid: SubjectId, database: Database):
    """Add a new metric."""
    data = get_data(database, report_uuid, subject_uuid)
    data.subject["metrics"][uuid()] = default_metric_attributes(database, report_uuid)
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid,
        description=f"{sessions.user(database)} added a new metric to subject '{data.subject_name}' in report "
                    f"'{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.delete("/report/<report_uuid>/metric/<metric_uuid>")
def delete_metric(report_uuid: ReportId, metric_uuid: MetricId, database: Database):
    """Delete a metric."""
    data = get_data(database, report_uuid, metric_uuid=metric_uuid)
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid,
        description=f"{sessions.user(database)} deleted metric '{data.metric_name}' from subject '{data.subject_name}' "
                    f"in report '{data.report_name}'.")
    del data.subject["metrics"][metric_uuid]
    return insert_new_report(database, data.report)


@bottle.post("/report/<report_uuid>/metric/<metric_uuid>/source/new")
def post_source_new(report_uuid: ReportId, metric_uuid: MetricId, database: Database):
    """Add a new source."""
    data = get_data(database, report_uuid, metric_uuid=metric_uuid)
    data_model = latest_datamodel(database)
    metric_type = data.metric["type"]
    source_type = data_model["metrics"][metric_type]["default_source"]
    parameters = default_source_parameters(database, metric_type, source_type)
    data.metric["sources"][uuid()] = dict(type=source_type, parameters=parameters)
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid, metric_uuid=metric_uuid,
        description=f"{sessions.user(database)} added a new source to metric '{data.metric_name}' of subject "
                    f"'{data.subject_name}' in report '{data.report_name}'.")
    return insert_new_report(database, data.report)


@bottle.delete("/report/<report_uuid>/source/<source_uuid>")
def delete_source(report_uuid: ReportId, source_uuid: SourceId, database: Database):
    """Delete a source."""
    data = get_data(database, report_uuid, source_uuid=source_uuid)
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid, metric_uuid=data.metric_uuid,
        description=f"{sessions.user(database)} deleted the source '{data.source_name}' from metric "
                    f"'{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}'.")
    del data.metric["sources"][source_uuid]
    return insert_new_report(database, data.report)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/<source_attribute>")
def post_source_attribute(report_uuid: ReportId, source_uuid: SourceId, source_attribute: str, database: Database):
    """Set a source attribute."""
    data = get_data(database, report_uuid, source_uuid=source_uuid)
    value = dict(bottle.request.json)[source_attribute]
    old_value = data.source.get(source_attribute) or ""
    data.source[source_attribute] = value
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid, metric_uuid=data.metric_uuid, source_uuid=source_uuid,
        description=f"{sessions.user(database)} changed the {source_attribute} of source '{data.source_name}' of "
                    f"metric '{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}' "
                    f"from '{old_value}' to '{value}'.")
    if source_attribute == "type":
        data.source["parameters"] = default_source_parameters(database, data.metric["type"], value)
    return insert_new_report(database, data.report)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/parameter/<parameter_key>")
def post_source_parameter(report_uuid: ReportId, source_uuid: SourceId, parameter_key: str, database: Database):
    """Set the source parameter."""
    data = get_data(database, report_uuid, source_uuid=source_uuid)
    parameter_value = dict(bottle.request.json)[parameter_key]
    old_value = data.source["parameters"].get(parameter_key) or ""
    new_value = data.source["parameters"][parameter_key] = parameter_value
    if data.datamodel["sources"][data.source["type"]]["parameters"][parameter_key]["type"] == "password":
        new_value, old_value = "*" * len(parameter_value), "*" * len(old_value)
    data.report["delta"] = dict(
        report_uuid=report_uuid, subject_uuid=data.subject_uuid, metric_uuid=data.metric_uuid, source_uuid=source_uuid,
        description=f"{sessions.user(database)} changed the {parameter_key} of source '{data.source_name}' of metric "
                    f"'{data.metric_name}' of subject '{data.subject_name}' in report '{data.report_name}' from "
                    f"'{old_value}' to '{new_value}'.")
    return insert_new_report(database, data.report)


@bottle.get("/reports")
def get_reports(database: Database):
    """Return the quality reports."""
    date_time = report_date_time()
    overview = latest_reports_overview(database, date_time)
    overview["reports"] = latest_reports(database, date_time)
    return overview


@bottle.post("/reports/<reports_attribute>")
def post_reports_attribute(reports_attribute: str, database: Database):
    """Set a reports overview attribute."""
    value = dict(bottle.request.json)[reports_attribute]
    overview = latest_reports_overview(database)
    overview[reports_attribute] = value
    return insert_new_reports_overview(database, overview)


@bottle.post("/report/new")
def post_report_new(database: Database):
    """Add a new report."""
    report = dict(report_uuid=uuid(), title="New report", subjects={})
    return insert_new_report(database, report)


@bottle.delete("/report/<report_uuid>")
def delete_report(report_uuid: ReportId, database: Database):
    """Delete a report."""
    report = latest_report(database, report_uuid)
    report["deleted"] = "true"
    return insert_new_report(database, report)


@bottle.get("/tagreport/<tag>")
def get_tag_report(tag: str, database: Database):
    """Get a report with all metrics that have the specified tag."""
    date_time = report_date_time()
    reports = latest_reports(database, date_time)
    subjects = dict()
    for report in reports:
        for subject_uuid, subject in list(report.get("subjects", {}).items()):
            for metric_uuid, metric in list(subject.get("metrics", {}).items()):
                if tag not in metric.get("tags", []):
                    del subject["metrics"][metric_uuid]
            if subject.get("metrics", {}):
                subjects[subject_uuid] = subject
    tag_report = dict(
        title=f'Report for tag "{tag}"', subtitle="Note: tag reports are read-only", report_uuid=f"tag-{tag}",
        timestamp=date_time, subjects=subjects)
    summarize_report(database, tag_report)
    return tag_report
