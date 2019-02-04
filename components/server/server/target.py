"""Target API."""

import logging

import bottle
import pymongo
from bson.objectid import ObjectId

from .measurement import determine_status
from .util import iso_timestamp


@bottle.post("/target/<measurement_id>")
def post_target(measurement_id: str, database):
    """Save the target for the metric."""
    target = bottle.request.json.get("target", "")
    measurement_doc = database.measurements.find_one(filter={"_id": ObjectId(measurement_id)})
    if not measurement_doc:
        logging.error("Can't find measurement with id %s to post target %s", measurement_id, target)
        return dict()
    del measurement_doc['_id']
    measurement_doc["measurement"]["target"] = target
    timestamp_string = iso_timestamp()
    measurement_doc["measurement"]["start"] = timestamp_string
    measurement_doc["measurement"]["end"] = timestamp_string
    value = measurement_doc["measurement"]["measurement"]
    metric_type = measurement_doc["metric"]["type"]
    direction = database.datamodel.find_one({})["metrics"][metric_type]["direction"]
    measurement_doc["measurement"]["status"] = determine_status(value, target, direction)
    database.measurements.insert_one(measurement_doc)
    return dict()
