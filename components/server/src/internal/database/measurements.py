"""Measurements collection."""
import pymongo
from pymongo.database import Database

from internal.model.measurement import Measurement
from internal.model.metric import Metric
from internal.server_utilities.functions import iso_timestamp
from internal.server_utilities.type import MeasurementId


def latest_measurement(database: Database, metric: Metric) -> Measurement | None:
    """Return the latest measurement."""
    latest = database.measurements.find_one(filter={"metric_uuid": metric.uuid}, sort=[("start", pymongo.DESCENDING)])
    return None if latest is None else Measurement(metric, latest)


def latest_successful_measurement(database: Database, metric: Metric) -> Measurement | None:
    """Return the latest successful measurement."""
    latest_successful = database.measurements.find_one(
        {"metric_uuid": metric.uuid, "has_error": False}, sort=[("start", pymongo.DESCENDING)]
    )
    return None if latest_successful is None else Measurement(metric, latest_successful)


def update_measurement_end(database: Database, measurement_id: MeasurementId):
    """Set the end date and time of the measurement to the current date and time."""
    return database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})


def insert_new_measurement(database: Database, measurement: Measurement) -> Measurement:
    """Insert a new measurement."""
    measurement.update_measurement()
    if "_id" in measurement:
        del measurement["_id"]  # Remove the Mongo ID if present so this measurement can be re-inserted in the database.
    database.measurements.insert_one(measurement)
    del measurement["_id"]
    return measurement
