"""Report routes."""

import bottle
import pymongo

from .util import iso_timestamp, report_date_time


@bottle.post("/report/title")
def post_report_title(database):
    """Set the report title."""
    title = bottle.request.json.get("title", "Quality-time")
    latest_report_doc = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del latest_report_doc["_id"]
    latest_report_doc["title"] = title
    latest_report_doc["timestamp"] = iso_timestamp()
    database.reports.insert(latest_report_doc)


@bottle.post("/report/subject/<subject_uuid>/title")
def post_subject_title(subject_uuid: str, database):
    """Set the subject title."""
    title = bottle.request.json.get("title", "<Unknown subject>")
    latest_report_doc = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del latest_report_doc["_id"]
    for subject in latest_report_doc["subject"]:
        if subject["uuid"] == subject_uuid:
            subject["title"] = title
            break
    latest_report_doc["timestamp"] = iso_timestamp()
    database.reports.insert(latest_report_doc)


@bottle.post("/report/subject/<subject_uuid>/metric/<metric_uuid>/source/<source_uuid>/url")
def post_source_url(subject_uuid: str, metric_uuid: str, source_uuid: str, database):
    """Set the source url."""
    url = bottle.request.json.get("url", "http://unknown")
    latest_report_doc = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del latest_report_doc["_id"]
    latest_report_doc["subjects"][subject_uuid]["metrics"][metric_uuid]["sources"][source_uuid]["url"] = url
    latest_report_doc["timestamp"] = iso_timestamp()
    database.reports.insert(latest_report_doc)


@bottle.get("/report")
def get_report(database):
    """Return the quality report."""
    latest_report_doc = database.reports.find_one(
        filter={"timestamp": {"$lt": report_date_time()}}, sort=[("timestamp", pymongo.DESCENDING)])
    latest_report_doc["_id"] = str(latest_report_doc["_id"])
    return latest_report_doc
