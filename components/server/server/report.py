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


@bottle.post("/report/subject/<subject_index>/title")
def post_subject_title(subject_index, database):
    """Set the subject title."""
    title = bottle.request.json.get("title", "<Unknown subject>")
    latest_report_doc = database.reports.find_one(filter={}, sort=[("timestamp", pymongo.DESCENDING)])
    del latest_report_doc["_id"]
    latest_report_doc["subjects"][int(subject_index)]["title"] = title
    latest_report_doc["timestamp"] = iso_timestamp()
    database.reports.insert(latest_report_doc)


@bottle.get("/report")
def get_report(database):
    """Return the quality report."""
    latest_report_doc = database.reports.find_one(
        filter={"timestamp": {"$lt": report_date_time()}}, sort=[("timestamp", pymongo.DESCENDING)])
    latest_report_doc["_id"] = str(latest_report_doc["_id"])
    return latest_report_doc
