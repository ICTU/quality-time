"""Target API."""

import datetime
import logging

import bottle
import pymongo

from .measurement import determine_status


@bottle.post("/target/<metric_name>/<source_name>")
def post_target(metric_name: str, source_name: str, database):
    """Save the target for the metric."""
    logging.info(bottle.request)
    target = bottle.request.json.get("target", "")
    urls = bottle.request.query.getall("url")  # pylint: disable=no-member
    components = bottle.request.query.getall("component")  # pylint: disable=no-member
    latest_measurement_doc = database.measurements.find_one(
        filter={"request.metric": metric_name, "request.source": source_name,
                "request.urls": urls, "request.components": components},
        sort=[("measurement.start", pymongo.DESCENDING)])
    if not latest_measurement_doc:
        logging.error("Can't find measurement for comment %s with parameters %s, %s, %s, %s",
                      target, metric_name, source_name, urls, components)
        return dict()
    del latest_measurement_doc['_id']
    latest_measurement_doc["measurement"]["target"] = target
    timestamp_string = datetime.datetime.now(datetime.timezone.utc).isoformat()
    latest_measurement_doc["measurement"]["start"] = timestamp_string
    latest_measurement_doc["measurement"]["end"] = timestamp_string
    value = latest_measurement_doc["measurement"]["measurement"]
    direction = latest_measurement_doc["metric"]["direction"]
    latest_measurement_doc["measurement"]["status"] = determine_status(value, target, direction)
    database.measurements.insert_one(latest_measurement_doc)
    return dict()
