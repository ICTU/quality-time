"""Comments API."""

import datetime
import logging

import bottle
import pymongo


@bottle.post("/comment/<metric_name>/<source_name>")
def post_comment(metric_name: str, source_name: str, database):
    """Save the comment for the metric."""
    logging.info(bottle.request)
    comment = bottle.request.json.get("comment", "")
    urls = bottle.request.query.getall("url")  # pylint: disable=no-member
    components = bottle.request.query.getall("component")  # pylint: disable=no-member
    latest_measurement_doc = database.measurements.find_one(
        filter={"request.metric": metric_name, "request.source": source_name,
                "request.urls": urls, "request.components": components},
        sort=[("measurement.start", pymongo.DESCENDING)])
    if not latest_measurement_doc:
        logging.error("Can't find measurement for comment %s with parameters %s, %s, %s, %s",
                      comment, metric_name, source_name, urls, components)
        return
    del latest_measurement_doc['_id']
    latest_measurement_doc["comment"] = comment
    timestamp_string = datetime.datetime.now(datetime.timezone.utc).isoformat()
    latest_measurement_doc["measurement"]["start"] = timestamp_string
    latest_measurement_doc["measurement"]["end"] = timestamp_string
    database.measurements.insert_one(latest_measurement_doc)
    return dict()
