"""Measurements collection."""

import pymongo
from pymongo.database import Database
from shared.utilities.functions import iso_timestamp
from shared.measurement.functions import calculate_measurement_value, determine_measurement_status

from .datamodels import latest_datamodel
from .reports import latest_metric


def latest_measurement(database: Database, metric_uuid: str):
    """Return the latest measurement."""
    return database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])


def last_measurements(database: Database, report_uuid: str):
    """Return the last measurement for each metric."""
    return database.measurements.find(filter={"report_uuid": report_uuid, "last": True})


def recent_measurements(database: Database, metric_uuid: str, max_iso_timestamp: str):
    """Return the recent measurements."""
    return database.measurements.find(filter={"metric_uuid": metric_uuid, "start": {"$lt": max_iso_timestamp}})


def count_measurements(database: Database, report_uuid: str) -> int:
    """Return the number of measurements."""
    return database.measurements.count_documents(filter={"report_uuid": report_uuid})


def insert_new_measurement(database: Database, measurement, metric=None):
    """Insert a new measurement."""
    measurement.pop("_id", None)
    metric = latest_metric(
        database, measurement["report_uuid"], measurement["metric_uuid"]) if metric is None else metric
    measurement["value"] = calculate_measurement_value(measurement["sources"], metric["addition"])
    datamodel = latest_datamodel(database)
    measurement["status"] = determine_measurement_status(datamodel, metric, measurement["value"])
    measurement["start"] = measurement["end"] = iso_timestamp()
    # Mark this measurement as the most recent one:
    measurement["last"] = True
    # And unset the last flag on the previous measurement(s):
    database.measurements.update_many(
        filter={"metric_uuid": measurement["metric_uuid"], "last": True}, update={"$unset": {"last": ""}})
    database.measurements.insert_one(measurement)
    measurement["_id"] = str(measurement["_id"])
    return measurement
