"""Report routes."""

import bottle
import pymongo

from .util import iso_timestamp, report_date_time, uuid


@bottle.post("/report/title")
def post_report_title(database):
    """Set the report title."""
    title = bottle.request.json.get("title", "Quality-time")
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["title"] = title
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)


@bottle.post("/report/subject/<subject_uuid>/title")
def post_subject_title(subject_uuid: str, database):
    """Set the subject title."""
    title = bottle.request.json["title"]
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["subjects"][subject_uuid]["title"] = title
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)


@bottle.post("/report/subject/new")
def post_new_subject(database):
    """Create a new subject."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    report["subjects"][uuid()] = dict(title="New subject", metrics={})
    database.reports.insert(report)


@bottle.delete("/report/subject/<subject_uuid>")
def delete_subject(subject_uuid: str, database):
    """Delete the subject."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    del report["subjects"][subject_uuid]
    database.reports.insert(report)


@bottle.get("/report/metrics")
def get_metrics(database):
    """Get all metrics."""
    report = database.reports.find_one(
        filter={"timestamp": {"$lt": report_date_time()}}, sort=[("timestamp", pymongo.DESCENDING)])
    metrics = {}
    for subject in report["subjects"].values():
        metrics.update(subject["metrics"])
    return metrics


@bottle.post("/report/metric/<metric_uuid>/type")
def post_metric_type(metric_uuid: str, database):
    """Set the metric type."""
    metric_type = bottle.request.json["type"]
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
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


@bottle.post("/report/metric/<metric_uuid>/<metric_attribute>")
def post_metric_attribute(metric_uuid: str, metric_attribute: str, database):
    """Set the metric attribute."""
    value = bottle.request.json[metric_attribute]
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            subject["metrics"][metric_uuid][metric_attribute] = value
            break
    database.reports.insert(report)


@bottle.post("/report/subject/<subject_uuid>/metric")
def post_metric_new(subject_uuid: str, database):
    """Add a new metric."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    subject = report["subjects"][subject_uuid]
    metric_type = list(database.datamodel.find_one({})["metrics"].keys())[0]
    subject["metrics"][uuid()] = dict(type=metric_type, sources={})
    database.reports.insert(report)


@bottle.delete("/report/metric/<metric_uuid>")
def delete_metric(metric_uuid: str, database):
    """Delete a metric."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            del subject["metrics"][metric_uuid]
    database.reports.insert(report)


@bottle.post("/report/metric/<metric_uuid>/source/new")
def post_source_new(metric_uuid: str, database):
    """Add a new source."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            metric = subject["metrics"][metric_uuid]
    metric_type = metric["type"]
    source_type = database.datamodel.find_one({})["metrics"][metric_type]["sources"][0]
    metric["sources"][uuid()] = dict(type=source_type)
    database.reports.insert(report)


@bottle.get("/report/sources/<metric_uuid>")
def get_sources_for_metric(metric_uuid: str, database):
    """Return the sources for the specified metric."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    for subject in report["subjects"].values():
        if metric_uuid in subject["metrics"]:
            return subject["metrics"][metric_uuid].get("sources", {})
    return {}


@bottle.delete("/report/source/<source_uuid>")
def delete_source(source_uuid: str, database):
    """Delete a source."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                del metric["sources"][source_uuid]
    database.reports.insert(report)


@bottle.post("/report/source/<source_uuid>/type")
def post_source_type(source_uuid: str, database):
    """Set the source type."""
    source_type = bottle.request.json["type"]
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
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
    for parameter in [key for key in source.keys() if key != "type"]:
        if parameter not in possible_parameters or metric_type not in possible_parameters[parameter]["metrics"]:
            del source[parameter]
    database.reports.insert(report)


@bottle.post("/report/source/<source_uuid>/<source_attr>")
def post_source_attr(source_uuid: str, source_attr: str, database):
    """Set the source attribute."""
    value = bottle.request.json[source_attr]
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if source_uuid in metric["sources"]:
                metric["sources"][source_uuid][source_attr] = value
                break
    database.reports.insert(report)


@bottle.get("/report")
def get_report(database):
    """Return the quality report."""
    report = database.reports.find_one(
        filter={"timestamp": {"$lt": report_date_time()}}, sort=[("timestamp", pymongo.DESCENDING)])
    report["_id"] = str(report["_id"])
    return report
