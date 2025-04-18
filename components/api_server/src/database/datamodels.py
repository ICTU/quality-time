"""Data models collection."""

import pymongo
from pymongo.database import Database

from shared.utils.functions import iso_timestamp


def latest_datamodel(database: Database, max_iso_timestamp: str = "") -> dict:
    """Return the latest data model."""
    timestamp_filter = {"timestamp": {"$lte": max_iso_timestamp}} if max_iso_timestamp else None
    if data_model := database.datamodels.find_one(timestamp_filter, sort=[("timestamp", pymongo.DESCENDING)]):
        data_model["_id"] = str(data_model["_id"])
    return data_model or {}


def insert_new_datamodel(database: Database, data_model: dict) -> None:  # pragma: no feature-test-cover
    """Insert a new data model in the data models collection."""
    data_model.pop("_id", None)
    data_model["timestamp"] = iso_timestamp()
    database.datamodels.insert_one(data_model)
