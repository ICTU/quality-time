"""Datamodels collection."""

from typing import Any, Dict, Optional

import pymongo

from ..util import iso_timestamp, uuid


def latest_datamodel(max_iso_timestamp: str, database):
    """Return the latest data model."""
    datamodel = database.datamodels.find_one(
        {"timestamp": {"$lte": max_iso_timestamp}}, sort=[("timestamp", pymongo.DESCENDING)])
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


def default_metric_attributes(report_uuid: str, metric_type: Optional[str], database):
    """Return the metric attributes with their default values for the specified metric type.
    If no metric type is specified, use the first one from the datamodel."""
    metric_types = latest_datamodel(iso_timestamp(), database)["metrics"]
    if not metric_type:
        metric_type = list(metric_types.keys())[0]
    defaults = metric_types[metric_type]
    return dict(
        type=metric_type, report_uuid=report_uuid, sources={}, name=None, unit=None,
        accept_debt=False, debt_target=None, target=defaults["target"], tags=defaults["tags"])


def default_subject_attributes(report_uuid: str, subject_type: Optional[str], database) -> Dict[str, Any]:
    """Return the default attributes for the subject."""
    subject_types = latest_datamodel(iso_timestamp(), database)["subjects"]
    if not subject_type:
        subject_type = list(subject_types.keys())[0]
    defaults = subject_types[subject_type]
    metrics = dict()
    for metric_type in defaults["metrics"]:
        metrics[uuid()] = default_metric_attributes(report_uuid, metric_type, database)
    return dict(
        type=subject_type, name=defaults["name"], description=defaults["description"],
        metrics=metrics)
