"""Datamodels collection."""

import pymongo

from ..util import iso_timestamp


def latest_datamodel(max_iso_timestamp: str, database):
    """Return the latest data model."""
    datamodel = database.datamodels.find_one(
        {"timestamp": {"$lt": max_iso_timestamp}}, sort=[("timestamp", pymongo.DESCENDING)])
    datamodel["_id"] = str(datamodel["_id"])
    return datamodel


def insert_new_datamodel(data_model, database):
    """Insert a new datamodel in the datamodels collection."""
    if "_id" in data_model:
        del data_model["_id"]
    data_model["timestamp"] = iso_timestamp()
    database.datamodels.insert_one(data_model)
