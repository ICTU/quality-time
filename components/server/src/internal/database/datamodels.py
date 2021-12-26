"""Data models collection."""

import pymongo
from pymongo.database import Database


def latest_datamodel(database: Database):
    """Return the latest data model."""
    if data_model := database.datamodels.find_one(sort=[("timestamp", pymongo.DESCENDING)]):  # pragma: no cover-behave
        data_model["_id"] = str(data_model["_id"])
    return data_model or {}
