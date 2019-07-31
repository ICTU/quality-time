"""Measurements collection."""

import pymongo
from pymongo.database import Database
from shared.database.reports import latest_metric
from shared.measurement.functions import calculate_measurement_value, determine_measurement_status
from shared.utilities.functions import iso_timestamp

from .datamodels import latest_datamodel


def latest_measurement(database: Database, metric_uuid: str):
    """Return the latest measurement."""
    return database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])


def update_measurement_end(database: Database, measurement_id: str):
    """Set the end date and time of the measurement to the current date and time."""
    # Setting last to true shouldn't be necessary in the long run because the last flag is set to true when a new
    # measurement is added. However, setting it here ensures the measurement collection is updated correctly after the
    # release of this code. This (setting last to true) was added in the version immediately after v0.5.1.
    return database.measurements.update_one(
        filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp(), "last": True}})


def insert_new_measurement(database: Database, measurement):
    """Insert a new measurement."""
    metric = latest_metric(database, measurement["report_uuid"], measurement["metric_uuid"])
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
