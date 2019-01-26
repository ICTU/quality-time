"""Comment API."""

import logging

import bottle
from bson.objectid import ObjectId

from .util import iso_timestamp


@bottle.post("/comment/<measurement_id>")
def post_comment(measurement_id: str, database):
    """Save the comment for the measurement."""
    comment = bottle.request.json.get("comment", "")
    measurement_doc = database.measurements.find_one(filter={"_id": ObjectId(measurement_id)})
    if not measurement_doc:
        logging.error("Can't find measurement with id %s to post comment %s", measurement_id, comment)
        return dict()
    del measurement_doc['_id']
    measurement_doc["comment"] = comment
    timestamp_string = iso_timestamp()
    measurement_doc["measurement"]["start"] = timestamp_string
    measurement_doc["measurement"]["end"] = timestamp_string
    database.measurements.insert_one(measurement_doc)
    return dict()
