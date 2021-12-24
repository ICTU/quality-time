"""Data models collection."""

import pymongo
from pymongo.database import Database


def latest_datamodel(database: Database, max_iso_timestamp: str = ""):
    """Return the latest data model."""
    timestamp_filter = dict(timestamp={"$lte": max_iso_timestamp}) if max_iso_timestamp else None
    if data_model := database.datamodels.find_one(timestamp_filter, sort=[("timestamp", pymongo.DESCENDING)]):
        data_model["_id"] = str(data_model["_id"])
    return data_model or {}
