"""Report routes."""

import bottle
import pymongo

from .util import iso_timestamp, report_date_time, uuid


def latest_report(report_uuid: str, database):
    """Return the latest report for the specifiekd report uuid."""
    return database.reports.find_one(filter={"report_uuid": report_uuid}, sort=[("timestamp", pymongo.DESCENDING)])


@bottle.post("/report/<report_uuid>/title")
def post_report_title(report_uuid: str, database):
    """Set the report title."""
    title = dict(bottle.request.json).get("title", "Quality-time")
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["title"] = title
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/title")
def post_subject_title(report_uuid: str, subject_uuid: str, database):
    """Set the subject title."""
    title = dict(bottle.request.json)["title"]
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["subjects"][subject_uuid]["title"] = title
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)


@bottle.post("/report/<report_uuid>/subject/new")
def post_new_subject(report_uuid: str, database):
    """Create a new subject."""
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    report["subjects"][uuid()] = dict(title="New subject", metrics={})
    database.reports.insert(report)


@bottle.delete("/report/<report_uuid>/subject/<subject_uuid>")
def delete_subject(report_uuid: str, subject_uuid: str, database):
    """Delete the subject."""
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    del report["subjects"][subject_uuid]
    database.reports.insert(report)


@bottle.get("/metrics")
def get_metrics(database):
    """Get all metrics."""
    metrics = {}
    reports = get_reports(database)
    for report in reports["reports"]:
        for subject in report["subjects"].values():
            metrics.update(subject["metrics"])
    return metrics


@bottle.post("/report/<report_uuid>/metric/<metric_uuid>/type")
def post_metric_type(report_uuid: str, metric_uuid: str, database):
    """Set the metric type."""
    metric_type = dict(bottle.request.json)["type"]
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            metric = subject["metrics"][metric_uuid]
            break
    metric["type"] = metric_type
    sources = metric["sources"]
    possible_sources = database.datamodel.find_one({})["metrics"][metric_type]["sources"]
    for source_uuid, source in list(sources.items()):
        if source["type"] not in possible_sources:
            del sources[source_uuid]
    database.reports.insert(report)


@bottle.post("/report/<report_uuid>/metric/<metric_uuid>/<metric_attribute>")
def post_metric_attribute(report_uuid: str, metric_uuid: str, metric_attribute: str, database):
    """Set the metric attribute."""
    value = dict(bottle.request.json)[metric_attribute]
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            subject["metrics"][metric_uuid][metric_attribute] = value
            break
    database.reports.insert(report)


@bottle.post("/report/<report_uuid>/subject/<subject_uuid>/metric")
def post_metric_new(report_uuid: str, subject_uuid: str, database):
    """Add a new metric."""
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    subject = report["subjects"][subject_uuid]
    metric_types = database.datamodel.find_one({})["metrics"]
    metric_type = list(metric_types.keys())[0]
    default_target = metric_types[metric_type]["default_target"]
    subject["metrics"][uuid()] = dict(type=metric_type, sources={}, report_uuid=report_uuid, target=default_target)
    database.reports.insert(report)


@bottle.delete("/report/<report_uuid>/metric/<metric_uuid>")
def delete_metric(report_uuid: str, metric_uuid: str, database):
    """Delete a metric."""
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            del subject["metrics"][metric_uuid]
    database.reports.insert(report)


@bottle.post("/report/<report_uuid>/metric/<metric_uuid>/source/new")
def post_source_new(report_uuid: str, metric_uuid: str, database):
    """Add a new source."""
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            metric = subject["metrics"][metric_uuid]
    metric_type = metric["type"]
    datamodel = database.datamodel.find_one({})
    source_type = datamodel["metrics"][metric_type]["sources"][0]
    parameters = dict()
    for parameter_key, parameter_value in datamodel["sources"][source_type]["parameters"].items():
        if metric_type in parameter_value["metrics"]:
            parameters[parameter_key] = ""
    metric["sources"][uuid()] = dict(type=source_type, parameters=parameters)
    database.reports.insert(report)


@bottle.delete("/report/<report_uuid>/source/<source_uuid>")
def delete_source(report_uuid: str, source_uuid: str, database):
    """Delete a source."""
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                del metric["sources"][source_uuid]
    database.reports.insert(report)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/type")
def post_source_type(report_uuid: str, source_uuid: str, database):
    """Set the source type."""
    source_type = dict(bottle.request.json)["type"]
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                source = metric["sources"][source_uuid]
                metric_type = metric["type"]
                break
    source["type"] = source_type
    possible_parameters = database.datamodel.find_one({})["sources"][source_type]["parameters"]
    for parameter in list(source["parameters"].keys()):
        if parameter not in possible_parameters or metric_type not in possible_parameters[parameter]["metrics"]:
            del source["parameters"][parameter]
    database.reports.insert(report)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/parameter/<parameter_key>")
def post_source_parameter(report_uuid: str, source_uuid: str, parameter_key: str, database):
    """Set the source parameter."""
    parameter_value = dict(bottle.request.json)[parameter_key]
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                metric["sources"][source_uuid]["parameters"][parameter_key] = parameter_value
                break
    database.reports.insert(report)


@bottle.post("/report/<report_uuid>/source/<source_uuid>/unit/<unit_key>/hide")
def hide_source_unit(report_uuid: str, source_uuid: str, unit_key: str, database):
    """Hide or unhide the source unit."""
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                source = metric["sources"][source_uuid]
                if "hidden_data" not in source:
                    source["hidden_data"] = []
                if unit_key in source["hidden_data"]:
                    source["hidden_data"].remove(unit_key)
                else:
                    source["hidden_data"].append(unit_key)
                break
    database.reports.insert(report)


@bottle.get("/reports")
def get_reports(database):
    """Return the quality reports."""
    report_uuids = database.reports.distinct("report_uuid")
    reports = []
    for report_uuid in report_uuids:
        report = database.reports.find_one(
            filter={"report_uuid": report_uuid, "timestamp": {"$lt": report_date_time()}},
            sort=[("timestamp", pymongo.DESCENDING)])
        if report and not "deleted" in report:
            report["_id"] = str(report["_id"])
            reports.append(report)
    return dict(reports=reports)


@bottle.post("/reports/new")
def post_report_new(database):
    """Add a new report."""
    report = dict(report_uuid=uuid(), title="New report", timestamp=iso_timestamp(), subjects={})
    database.reports.insert(report)


@bottle.delete("/report/<report_uuid>")
def delete_report(report_uuid: str, database):
    """Delete a report."""
    report = latest_report(report_uuid, database)
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    report["deleted"] = "true"
    database.reports.insert(report)
