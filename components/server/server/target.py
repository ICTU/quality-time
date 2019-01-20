"""Target API."""

import logging

import bottle
import pymongo

from .measurement import determine_status
from .util import iso_timestamp


@bottle.post("/target/<metric_name>")
def post_target(metric_name: str, database):
    """Save the target for the metric."""
    target = bottle.request.json.get("target", "")
    sources = bottle.request.query.getall("source")  # pylint: disable=no-member
    urls = bottle.request.query.getall("url")  # pylint: disable=no-member
    components = bottle.request.query.getall("component")  # pylint: disable=no-member
    latest_measurement_doc = database.measurements.find_one(
        filter={"request.metric": metric_name, "request.sources": sources,
                "request.urls": urls, "request.components": components},
        sort=[("measurement.start", pymongo.DESCENDING)])
    if not latest_measurement_doc:
        logging.error("Can't find measurement for comment %s with parameters %s, %s, %s, %s",
                      target, metric_name, sources, urls, components)
        return dict()
    del latest_measurement_doc['_id']
    latest_measurement_doc["measurement"]["target"] = target
    timestamp_string = iso_timestamp()
    latest_measurement_doc["measurement"]["start"] = timestamp_string
    latest_measurement_doc["measurement"]["end"] = timestamp_string
    value = latest_measurement_doc["measurement"]["measurement"]
    metric = database.metrics.find_one(filter={"metric": latest_measurement_doc["request"]["metric"]})
    latest_measurement_doc["measurement"]["status"] = determine_status(value, target, metric["direction"])
    database.measurements.insert_one(latest_measurement_doc)
    return dict()
