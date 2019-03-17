"""Datamodels collection."""

import pymongo

from ..util import iso_timestamp


def latest_datamodel(max_iso_timestamp: str, database):
    """Return the latest data model."""
    datamodel = database.datamodels.find_one(
        {"timestamp": {"$lt": max_iso_timestamp}}, sort=[("timestamp", pymongo.DESCENDING)])
    if datamodel:
        datamodel["_id"] = str(datamodel["_id"])
    return datamodel


def insert_new_datamodel(data_model, database):
    """Insert a new datamodel in the datamodels collection."""
    if "_id" in data_model:
        del data_model["_id"]
    data_model["timestamp"] = iso_timestamp()
    database.datamodels.insert_one(data_model)


def default_source_parameters(metric_type: str, source_type: str, database):
    """Return the source parameters with their default values for the specified metric."""
    datamodel = latest_datamodel(iso_timestamp(), database)
    parameters = dict()
    for parameter_key, parameter_value in datamodel["sources"][source_type]["parameters"].items():
        if metric_type in parameter_value["metrics"]:
            parameters[parameter_key] = parameter_value["default_value"]
    return parameters
