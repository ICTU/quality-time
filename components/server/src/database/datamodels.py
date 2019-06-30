"""Datamodels collection."""

from typing import Any, Dict

import pymongo
from pymongo.database import Database

from ..util import iso_timestamp


def latest_datamodel(database: Database, max_iso_timestamp: str = ""):
    """Return the latest data model."""
    datamodel = database.datamodels.find_one(
        {"timestamp": {"$lte": max_iso_timestamp or iso_timestamp()}}, sort=[("timestamp", pymongo.DESCENDING)])
    if datamodel:
        datamodel["_id"] = str(datamodel["_id"])
    return datamodel or dict()


def insert_new_datamodel(database: Database, data_model):
    """Insert a new datamodel in the datamodels collection."""
    if "_id" in data_model:
        del data_model["_id"]
    data_model["timestamp"] = iso_timestamp()
    return database.datamodels.insert_one(data_model)


def default_source_parameters(database: Database, metric_type: str, source_type: str):
    """Return the source parameters with their default values for the specified metric."""
    datamodel = latest_datamodel(database)
    parameters = dict()
    for parameter_key, parameter_value in datamodel["sources"][source_type]["parameters"].items():
        if metric_type in parameter_value["metrics"]:
            parameters[parameter_key] = parameter_value["default_value"]
    return parameters


def default_metric_attributes(database: Database, report_uuid: str, metric_type: str = ""):
    """Return the metric attributes with their default values for the specified metric type.
    If no metric type is specified, use the first one from the datamodel."""
    metric_types = latest_datamodel(database)["metrics"]
    if not metric_type:
        metric_type = list(metric_types.keys())[0]
    defaults = metric_types[metric_type]
    return dict(
        type=metric_type, report_uuid=report_uuid, sources={}, name=None, unit=None, addition=defaults["addition"],
        accept_debt=False, debt_target=None, target=defaults["target"], near_target=defaults["near_target"],
        tags=defaults["tags"])


def default_subject_attributes(database: Database, subject_type: str = "") -> Dict[str, Any]:
    """Return the default attributes for the subject."""
    subject_types = latest_datamodel(database)["subjects"]
    if not subject_type:
        subject_type = list(subject_types.keys())[0]
    defaults = subject_types[subject_type]
    return dict(type=subject_type, name=defaults["name"], description=defaults["description"], metrics=dict())
