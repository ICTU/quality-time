"""Report routes."""

from typing import Any, Dict

from pymongo.database import Database
import bottle

from ..database.reports import latest_reports, latest_report, insert_new_report
from ..database.datamodels import latest_datamodel, default_subject_attributes, default_metric_attributes, \
    default_source_parameters
from ..util import report_date_time, uuid
from .measurement import latest_measurement, insert_new_measurement


def get_metric(report, metric_uuid: str):
    """Return the metric with the specified uuid."""
    return [subject["metrics"][metric_uuid] for subject in report["subjects"].values()
            if metric_uuid in subject["metrics"]][0]


@bottle.post("/report/<report_uuid>/title")
def post_report_title(report_uuid: str, database: Database):
    """Set the report title."""
    title = dict(bottle.request.json).get("title", "Quality-time")
    report = latest_report(database, report_uuid)
    report["title"] = title
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/<subject_attribute>")
def post_subject_attribute(report_uuid: str, subject_uuid: str, subject_attribute: str, database: Database):
    """Set the subject attribute."""
    value = dict(bottle.request.json)[subject_attribute]
    report = latest_report(database, report_uuid)
    subject = report["subjects"][subject_uuid]
    subject[subject_attribute] = value
    if subject_attribute == "type":
        default_metric_types = latest_datamodel(database)["subjects"][value]["metrics"]
        existing_metric_types = [metric["type"] for metric in subject["metrics"].values()]
        for default_metric_type in default_metric_types:
            if default_metric_type not in existing_metric_types:
                subject["metrics"][uuid()] = default_metric_attributes(database, report_uuid, default_metric_type)
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/subject/new")
def post_new_subject(report_uuid: str, database: Database):
    """Create a new subject."""
    report = latest_report(database, report_uuid)
    report["subjects"][uuid()] = default_subject_attributes(database, report_uuid)
    return insert_new_report(database, report)


@bottle.delete("/report/<report_uuid>/subject/<subject_uuid>")
def delete_subject(report_uuid: str, subject_uuid: str, database: Database):
    """Delete the subject."""
    report = latest_report(database, report_uuid)
    del report["subjects"][subject_uuid]
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
    metric[metric_attribute] = value
    if metric_attribute == "type":
        metric.update(default_metric_attributes(database, report_uuid, value))
    insert_new_report(database, report)
    if metric_attribute in ("accept_debt", "debt_target", "near_target", "target"):
        latest = latest_measurement(database, metric_uuid)
        if latest:
            return insert_new_measurement(database, latest, metric)
    return dict(ok=True)


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/metric/new")
def post_metric_new(report_uuid: str, subject_uuid: str, database: Database):
    """Add a new metric."""
    report = latest_report(database, report_uuid)
    subject = report["subjects"][subject_uuid]
    subject["metrics"][uuid()] = default_metric_attributes(database, report_uuid)
    return insert_new_report(database, report)


@bottle.delete("/report/<report_uuid>/metric/<metric_uuid>")
def delete_metric(report_uuid: str, metric_uuid: str, database: Database):
    """Delete a metric."""
    report = latest_report(database, report_uuid)
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            del subject["metrics"][metric_uuid]
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/metric/<metric_uuid>/source/new")
def post_source_new(report_uuid: str, metric_uuid: str, database: Database):
    """Add a new source."""
    report = latest_report(database, report_uuid)
    metric = get_metric(report, metric_uuid)
    metric_type = metric["type"]
    datamodel = latest_datamodel(database)
    source_type = datamodel["metrics"][metric_type]["sources"][0]
    parameters = default_source_parameters(database, metric_type, source_type)
    metric["sources"][uuid()] = dict(type=source_type, parameters=parameters)
    return insert_new_report(database, report)


@bottle.delete("/report/<report_uuid>/source/<source_uuid>")
def delete_source(report_uuid: str, source_uuid: str, database: Database):
    """Delete a source."""
    report = latest_report(database, report_uuid)
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                del metric["sources"][source_uuid]
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/<source_attribute>")
def post_source_attribute(report_uuid: str, source_uuid: str, source_attribute: str, database: Database):
    """Set a source attribute."""
    value = dict(bottle.request.json)[source_attribute]
    report = latest_report(database, report_uuid)
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                source = metric["sources"][source_uuid]
                metric_type = metric["type"]
                break
    source[source_attribute] = value
    if source_attribute == "type":
        source["parameters"] = default_source_parameters(database, metric_type, value)
    return insert_new_report(database, report)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/parameter/<parameter_key>")
def post_source_parameter(report_uuid: str, source_uuid: str, parameter_key: str, database: Database):
    """Set the source parameter."""
    parameter_value = dict(bottle.request.json)[parameter_key]
    report = latest_report(database, report_uuid)
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                metric["sources"][source_uuid]["parameters"][parameter_key] = parameter_value
                break
    return insert_new_report(database, report)


@bottle.get("/reports")
def get_reports(database: Database):
    """Return the quality reports."""
    return dict(reports=latest_reports(database, report_date_time()))


@bottle.post("/reports/new")
def post_report_new(database: Database):
    """Add a new report."""
    report = dict(report_uuid=uuid(), title="New report", subjects={})
    return insert_new_report(database, report)


@bottle.delete("/report/<report_uuid>")
def delete_report(report_uuid: str, database: Database):
    """Delete a report."""
    report = latest_report(database, report_uuid)
    report["deleted"] = "true"
    return insert_new_report(database, report)
