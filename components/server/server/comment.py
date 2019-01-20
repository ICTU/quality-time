"""Comment API."""

import logging

import bottle
import pymongo

from .util import iso_timestamp


@bottle.post("/comment/<metric_name>")
def post_comment(metric_name: str, database):
    """Save the comment for the metric."""
    comment = bottle.request.json.get("comment", "")
    sources = bottle.request.query.getall("source")  # pylint: disable=no-member
    urls = bottle.request.query.getall("url")  # pylint: disable=no-member
    components = bottle.request.query.getall("component")  # pylint: disable=no-member
    latest_measurement_doc = database.measurements.find_one(
        filter={"request.metric": metric_name, "request.sources": sources,
                "request.urls": urls, "request.components": components},
        sort=[("measurement.start", pymongo.DESCENDING)])
    if not latest_measurement_doc:
        logging.error("Can't find measurement for comment %s with parameters %s, %s, %s, %s",
                      comment, metric_name, sources, urls, components)
        return dict()
    del latest_measurement_doc['_id']
    latest_measurement_doc["comment"] = comment
    timestamp_string = iso_timestamp()
    latest_measurement_doc["measurement"]["start"] = timestamp_string
    latest_measurement_doc["measurement"]["end"] = timestamp_string
    database.measurements.insert_one(latest_measurement_doc)
    return dict()
