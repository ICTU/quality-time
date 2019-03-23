"""Report routes."""

import bottle

from ..database.reports import latest_reports, latest_report, insert_new_report
from ..database.datamodels import latest_datamodel, default_source_parameters
from ..util import iso_timestamp, report_date_time, uuid
from .measurement import latest_measurement, insert_new_measurement


@bottle.post("/report/<report_uuid>/title")
def post_report_title(report_uuid: str, database):
    """Set the report title."""
    title = dict(bottle.request.json).get("title", "Quality-time")
    report = latest_report(report_uuid, database)
    report["title"] = title
    return insert_new_report(report, database)


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/title")
def post_subject_title(report_uuid: str, subject_uuid: str, database):
    """Set the subject title."""
    title = dict(bottle.request.json)["title"]
    report = latest_report(report_uuid, database)
    report["subjects"][subject_uuid]["title"] = title
    return insert_new_report(report, database)


@bottle.post("/report/<report_uuid>/subject/new")
def post_new_subject(report_uuid: str, database):
    """Create a new subject."""
    report = latest_report(report_uuid, database)
    report["subjects"][uuid()] = dict(title="New subject", metrics={})
    return insert_new_report(report, database)


@bottle.delete("/report/<report_uuid>/subject/<subject_uuid>")
def delete_subject(report_uuid: str, subject_uuid: str, database):
    """Delete the subject."""
    report = latest_report(report_uuid, database)
    del report["subjects"][subject_uuid]
    return insert_new_report(report, database)


@bottle.get("/metrics")
def get_metrics(database):
    """Get all metrics."""
    metrics = {}
    reports = get_reports(database)
    for report in reports["reports"]:
        for subject in report["subjects"].values():
            metrics.update(subject["metrics"])
    return metrics


@bottle.post("/report/<report_uuid>/metric/<metric_uuid>/<metric_attribute>")
def post_metric_attribute(report_uuid: str, metric_uuid: str, metric_attribute: str, database):
    """Set the metric attribute."""
    value = dict(bottle.request.json)[metric_attribute]
    report = latest_report(report_uuid, database)
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            metric = subject["metrics"][metric_uuid]
            break
    metric[metric_attribute] = value
    if metric_attribute == "type":
        sources = metric["sources"]
        possible_sources = latest_datamodel(iso_timestamp(), database)["metrics"][value]["sources"]
        for source_uuid, source in list(sources.items()):
            if source["type"] not in possible_sources:
                del sources[source_uuid]
    insert_new_report(report, database)
    if metric_attribute in ("accept_debt", "debt_target", "target"):
        latest = latest_measurement(metric_uuid, database)
        if latest:
            return insert_new_measurement(metric_uuid, latest, database, **{metric_attribute: value})
    return dict(ok=True)


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/metric")
def post_metric_new(report_uuid: str, subject_uuid: str, database):
    """Add a new metric."""
    report = latest_report(report_uuid, database)
    subject = report["subjects"][subject_uuid]
    metric_types = latest_datamodel(iso_timestamp(), database)["metrics"] # {"violations": {...}, "size": {...}}
    metric_type = list(metric_types.keys())[0]  # metric_types.keys()[0] = ["violations", "size", ...][0] == "violations"
    default_target = metric_types[metric_type]["default_target"]  # {"violations": {"default_target": 0, ...}}
    default_tags = metric_types[metric_type]["tags"]
    subject["metrics"][uuid()] = dict(
        type=metric_type, sources={}, report_uuid=report_uuid, name=None, unit=None,
        target=default_target, accept_debt=False, debt_target=None, tags=default_tags)
    return insert_new_report(report, database)


@bottle.delete("/report/<report_uuid>/metric/<metric_uuid>")
def delete_metric(report_uuid: str, metric_uuid: str, database):
    """Delete a metric."""
    report = latest_report(report_uuid, database)
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            del subject["metrics"][metric_uuid]
    return insert_new_report(report, database)


@bottle.post("/report/<report_uuid>/metric/<metric_uuid>/source/new")
def post_source_new(report_uuid: str, metric_uuid: str, database):
    """Add a new source."""
    report = latest_report(report_uuid, database)
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            metric = subject["metrics"][metric_uuid]
    metric_type = metric["type"]
    datamodel = latest_datamodel(iso_timestamp(), database)
    source_type = datamodel["metrics"][metric_type]["sources"][0]
    parameters = default_source_parameters(metric_type, source_type, database)
    metric["sources"][uuid()] = dict(type=source_type, parameters=parameters)
    return insert_new_report(report, database)


@bottle.delete("/report/<report_uuid>/source/<source_uuid>")
def delete_source(report_uuid: str, source_uuid: str, database):
    """Delete a source."""
    report = latest_report(report_uuid, database)
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                del metric["sources"][source_uuid]
    return insert_new_report(report, database)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/<source_attribute>")
def post_source_attribute(report_uuid: str, source_uuid: str, source_attribute: str, database):
    """Set a source attribute."""
    value = dict(bottle.request.json)[source_attribute]
    report = latest_report(report_uuid, database)
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                source = metric["sources"][source_uuid]
                metric_type = metric["type"]
                break
    source[source_attribute] = value
    if source_attribute == "type":
        source["parameters"] = default_source_parameters(metric_type, value, database)
    return insert_new_report(report, database)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/parameter/<parameter_key>")
def post_source_parameter(report_uuid: str, source_uuid: str, parameter_key: str, database):
    """Set the source parameter."""
    parameter_value = dict(bottle.request.json)[parameter_key]
    report = latest_report(report_uuid, database)
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                metric["sources"][source_uuid]["parameters"][parameter_key] = parameter_value
                break
    return insert_new_report(report, database)


@bottle.get("/reports")
def get_reports(database):
    """Return the quality reports."""
    return dict(reports=latest_reports(report_date_time(), database))


@bottle.post("/reports/new")
def post_report_new(database):
    """Add a new report."""
    report = dict(report_uuid=uuid(), title="New report", subjects={})
    return insert_new_report(report, database)


@bottle.delete("/report/<report_uuid>")
def delete_report(report_uuid: str, database):
    """Delete a report."""
    report = latest_report(report_uuid, database)
    report["deleted"] = "true"
    return insert_new_report(report, database)
