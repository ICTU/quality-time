"""Report routes."""

from typing import Any, Dict

import bottle
from pymongo.database import Database

from database.datamodels import (
    latest_datamodel, default_subject_attributes, default_metric_attributes, default_source_parameters
)
from database.reports import (
    latest_reports, latest_report, insert_new_report, latest_reports_overview, insert_new_reports_overview,
    summarize_report
)
from database import sessions
from utilities.functions import report_date_time, uuid
from .measurement import latest_measurement, insert_new_measurement


def get_subject(report, metric_uuid: str):
    """Return the subject that has the metric with the specified uuid."""
    return [subject for subject in report["subjects"].values() if metric_uuid in subject["metrics"]][0]


def get_metric(report, metric_uuid: str):
    """Return the metric with the specified uuid."""
    return [subject["metrics"][metric_uuid] for subject in report["subjects"].values()
            if metric_uuid in subject["metrics"]][0]


def get_metric_by_source_uuid(report, source_uuid: str):
    """Return the metric that has a source with the specified uuid."""
    return [metric for subject in report["subjects"].values() for metric in subject["metrics"].values()
            if source_uuid in metric["sources"]][0]


def get_subject_name(subject, database: Database):
    """Return the subject name."""
    return subject.get("name") or latest_datamodel(database)["subjects"][subject["type"]]["name"]


def get_metric_name(metric, database: Database):
    """Return the metric name."""
    return metric.get("name") or latest_datamodel(database)["metrics"][metric["type"]]["name"]


def get_source_name(source, database: Database):
    """Return the source name."""
    return source.get("name") or latest_datamodel(database)["sources"][source["type"]]["name"]


@bottle.post("/report/<report_uuid>/<report_attribute>")
def post_report_attribute(report_uuid: str, report_attribute: str, database: Database):
    """Set a report attribute."""
    report = latest_report(database, report_uuid)
    value = dict(bottle.request.json)[report_attribute]
    old_value = report.get(report_attribute) or ""
    report[report_attribute] = value
    report["delta"] = \
        f"{sessions.user(database)} changed the report {report_attribute} from '{old_value}' to '{value}'."
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/<subject_attribute>")
def post_subject_attribute(report_uuid: str, subject_uuid: str, subject_attribute: str, database: Database):
    """Set the subject attribute."""
    value = dict(bottle.request.json)[subject_attribute]
    report = latest_report(database, report_uuid)
    subject = report["subjects"][subject_uuid]
    name = get_subject_name(subject, database)
    old_value = subject.get(subject_attribute) or ""
    subject[subject_attribute] = value
    report["delta"] = \
        f"{sessions.user(database)} changed the {subject_attribute} of subject {name} from '{old_value}' to '{value}'."
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/subject/new")
def post_new_subject(report_uuid: str, database: Database):
    """Create a new subject."""
    report = latest_report(database, report_uuid)
    report["subjects"][uuid()] = default_subject_attributes(database)
    report["delta"] = f"{sessions.user(database)} created a new subject."
    return insert_new_report(database, report)


@bottle.delete("/report/<report_uuid>/subject/<subject_uuid>")
def delete_subject(report_uuid: str, subject_uuid: str, database: Database):
    """Delete the subject."""
    report = latest_report(database, report_uuid)
    subject = report["subjects"][subject_uuid]
    name = get_subject_name(subject, database)
    del report["subjects"][subject_uuid]
    report["delta"] = f"{sessions.user(database)} deleted the subject {name}."
    return insert_new_report(database, report)


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
def post_metric_attribute(report_uuid: str, metric_uuid: str, metric_attribute: str, database: Database):
    """Set the metric attribute."""
    value = dict(bottle.request.json)[metric_attribute]
    report = latest_report(database, report_uuid)
    metric = get_metric(report, metric_uuid)
    name = get_metric_name(metric, database)
    old_value = metric.get(metric_attribute) or ""
    metric[metric_attribute] = value
    if metric_attribute == "type":
        metric.update(default_metric_attributes(database, report_uuid, value))
    report["delta"] = \
        f"{sessions.user(database)} changed the {metric_attribute} of metric {name} from '{old_value}' to '{value}'."
    insert_new_report(database, report)
    if metric_attribute in ("accept_debt", "debt_target", "debt_end_date", "near_target", "target"):
        latest = latest_measurement(database, metric_uuid)
        if latest:
            return insert_new_measurement(database, latest, metric)
    return dict(ok=True)


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/metric/new")
def post_metric_new(report_uuid: str, subject_uuid: str, database: Database):
    """Add a new metric."""
    report = latest_report(database, report_uuid)
    subject = report["subjects"][subject_uuid]
    name = subject.get("name") or latest_datamodel(database)["subjects"][subject["type"]]["name"]
    subject["metrics"][uuid()] = default_metric_attributes(database, report_uuid)
    report["delta"] = f"{sessions.user(database)} added a metric to subject {name}."
    return insert_new_report(database, report)


@bottle.delete("/report/<report_uuid>/metric/<metric_uuid>")
def delete_metric(report_uuid: str, metric_uuid: str, database: Database):
    """Delete a metric."""
    report = latest_report(database, report_uuid)
    subject = get_subject(report, metric_uuid)
    metric = subject["metrics"][metric_uuid]
    subject_name = get_subject_name(subject, database)
    metric_name = get_metric_name(metric, database)
    report["delta"] = f"{sessions.user(database)} deleted metric {metric_name} from subject {subject_name}."
    del subject["metrics"][metric_uuid]
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/metric/<metric_uuid>/source/new")
def post_source_new(report_uuid: str, metric_uuid: str, database: Database):
    """Add a new source."""
    report = latest_report(database, report_uuid)
    metric = get_metric(report, metric_uuid)
    metric_type = metric["type"]
    datamodel = latest_datamodel(database)
    source_type = datamodel["metrics"][metric_type]["default_source"]
    parameters = default_source_parameters(database, metric_type, source_type)
    name = get_metric_name(metric, database)
    metric["sources"][uuid()] = dict(type=source_type, parameters=parameters)
    report["delta"] = f"{sessions.user(database)} added a new source to metric {name}."
    return insert_new_report(database, report)


@bottle.delete("/report/<report_uuid>/source/<source_uuid>")
def delete_source(report_uuid: str, source_uuid: str, database: Database):
    """Delete a source."""
    report = latest_report(database, report_uuid)
    metric = get_metric_by_source_uuid(report, source_uuid)
    source = metric["sources"][source_uuid]
    source_name = get_source_name(source, database)
    metric_name = get_metric_name(metric, database)
    report["delta"] = f"{sessions.user(database)} deleted the source {source_name} from metric {metric_name}."
    del metric["sources"][source_uuid]
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/<source_attribute>")
def post_source_attribute(report_uuid: str, source_uuid: str, source_attribute: str, database: Database):
    """Set a source attribute."""
    value = dict(bottle.request.json)[source_attribute]
    report = latest_report(database, report_uuid)
    metric = get_metric_by_source_uuid(report, source_uuid)
    source = metric["sources"][source_uuid]
    name = get_source_name(source, database)
    old_value = source.get(source_attribute) or ""
    source[source_attribute] = value
    report["delta"] = \
        f"{sessions.user(database)} changed the {source_attribute} of source {name} from '{old_value}' to '{value}'."
    if source_attribute == "type":
        source["parameters"] = default_source_parameters(database, metric["type"], value)
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/parameter/<parameter_key>")
def post_source_parameter(report_uuid: str, source_uuid: str, parameter_key: str, database: Database):
    """Set the source parameter."""
    parameter_value = dict(bottle.request.json)[parameter_key]
    report = latest_report(database, report_uuid)
    metric = get_metric_by_source_uuid(report, source_uuid)
    source = metric["sources"][source_uuid]
    old_value = source["parameters"].get(parameter_key) or ""
    name = get_source_name(source, database)
    source["parameters"][parameter_key] = parameter_value
    report["delta"] = \
        f"{sessions.user(database)} changed the {parameter_key} of source {name} from '{old_value}' to " \
        f"'{parameter_value}'."
    return insert_new_report(database, report)


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
    report = dict(
        report_uuid=uuid(), title="New report", subjects={}, delta=f"{sessions.user(database)} created a new report.")
    return insert_new_report(database, report)


@bottle.delete("/report/<report_uuid>")
def delete_report(report_uuid: str, database: Database):
    """Delete a report."""
    report = latest_report(database, report_uuid)
    report["deleted"] = "true"
    report["delta"] = f"{sessions.user(database)} deleted the report {report['title']}."
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
