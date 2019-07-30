"""Datamodels collection."""

import pymongo
from pymongo.database import Database


def latest_datamodel(database: Database):
    """Return the latest data model."""
    datamodel = database.datamodels.find_one(sort=[("timestamp", pymongo.DESCENDING)])
    datamodel["_id"] = str(datamodel["_id"])
    return datamodel
