"""Datamodels collection."""

import pymongo
from pymongo.database import Database

from utilities.functions import iso_timestamp


def latest_datamodel(database: Database):
    """Return the latest data model."""
    datamodel = database.datamodels.find_one(
        {"timestamp": {"$lte": iso_timestamp()}}, sort=[("timestamp", pymongo.DESCENDING)])
    datamodel["_id"] = str(datamodel["_id"])
    return datamodel
