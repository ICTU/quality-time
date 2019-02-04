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


@bottle.post("/report/subject/<subject_uuid>/metric/<metric_uuid>/type")
def post_metric_type(subject_uuid: str, metric_uuid: str, database):
    """Set the metric type."""
    metric_type = bottle.request.json["type"]
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    metric = report["subjects"][subject_uuid]["metrics"][metric_uuid]
    metric["type"] = metric_type
    sources = metric["sources"]
    possible_sources = database.datamodel.find_one({})["metrics"][metric_type]["sources"]
    for source_uuid, source in list(sources.items()):
        if source["type"] not in possible_sources:
            del sources[source_uuid]
    database.reports.insert(report)


@bottle.post("/report/subject/<subject_uuid>/metric/<metric_uuid>/comment")
def post_metric_comment(subject_uuid: str, metric_uuid: str, database):
    """Set the metric comment."""
    metric_comment = bottle.request.json["comment"]
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    metric = report["subjects"][subject_uuid]["metrics"][metric_uuid]
    metric["comment"] = metric_comment
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


@bottle.delete("/report/subject/<subject_uuid>/metric/<metric_uuid>")
def post_metric_delete(subject_uuid: str, metric_uuid: str, database):
    """Delete a metric."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    del report["subjects"][subject_uuid]["metrics"][metric_uuid]
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)


@bottle.post("/report/subject/<subject_uuid>/metric/<metric_uuid>/source")
def post_source_new(subject_uuid: str, metric_uuid: str, database):
    """Add a new source."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    metric = report["subjects"][subject_uuid]["metrics"][metric_uuid]
    metric_type = metric["type"]
    source_type = database.datamodel.find_one({})["metrics"][metric_type]["sources"][0]
    metric["sources"][uuid()] = dict(type=source_type)
    database.reports.insert(report)


@bottle.delete("/report/subject/<subject_uuid>/metric/<metric_uuid>/source/<source_uuid>")
def post_source_delete(subject_uuid: str, metric_uuid: str, source_uuid: str, database):
    """Delete a source."""
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    del report["subjects"][subject_uuid]["metrics"][metric_uuid]["sources"][source_uuid]
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)


@bottle.post("/report/subject/<subject_uuid>/metric/<metric_uuid>/source/<source_uuid>/type")
def post_source_type(subject_uuid: str, metric_uuid: str, source_uuid: str, database):
    """Set the source type."""
    source_type = bottle.request.json["type"]
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["timestamp"] = iso_timestamp()
    metric = report["subjects"][subject_uuid]["metrics"][metric_uuid]
    metric_type = metric["type"]
    source = metric["sources"][source_uuid]
    source["type"] = source_type
    possible_parameters = database.datamodel.find_one({})["sources"][source_type]["parameters"]
    for parameter in [key for key in source.keys() if key != "type"]:
        if parameter not in possible_parameters or metric_type not in possible_parameters[parameter]["metrics"]:
            del source[parameter]
    database.reports.insert(report)


@bottle.post("/report/subject/<subject_uuid>/metric/<metric_uuid>/source/<source_uuid>/<source_attr>")
def post_source_attr(subject_uuid: str, metric_uuid: str, source_uuid: str, source_attr: str, database):
    """Set the source attribute."""
    value = bottle.request.json[source_attr]
    report = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del report["_id"]
    report["subjects"][subject_uuid]["metrics"][metric_uuid]["sources"][source_uuid][source_attr] = value
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)


@bottle.get("/report")
def get_report(database):
    """Return the quality report."""
    report = database.reports.find_one(
        filter={"timestamp": {"$lt": report_date_time()}}, sort=[("timestamp", pymongo.DESCENDING)])
    report["_id"] = str(report["_id"])
    return report
