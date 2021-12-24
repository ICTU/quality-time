"""Data models collection."""

import pymongo
from pymongo.database import Database

from server_utilities.functions import iso_timestamp


def latest_datamodel(database: Database, max_iso_timestamp: str = ""):
    """Return the latest data model."""
    timestamp_filter = dict(timestamp={"$lte": max_iso_timestamp}) if max_iso_timestamp else None
    if data_model := database.datamodels.find_one(timestamp_filter, sort=[("timestamp", pymongo.DESCENDING)]):
        data_model["_id"] = str(data_model["_id"])
    return data_model or {}


def insert_new_datamodel(database: Database, data_model):
    """Insert a new data model in the data models collection."""
    if "_id" in data_model:  # pragma: no cover-behave
        del data_model["_id"]
    data_model["timestamp"] = iso_timestamp()
    return database.datamodels.insert_one(data_model)
