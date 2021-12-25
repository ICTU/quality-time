"""Measurements collection."""

import pymongo
from pymongo.database import Database

from server_utilities.functions import iso_timestamp
from server_utilities.type import MeasurementId
from shared.model.measurement import Measurement
from shared.model.metric import Metric


def latest_successful_measurement(database: Database, metric: Metric) -> Measurement | None:
    """Return the latest successful measurement."""
    latest_successful = database.measurements.find_one(
        {"metric_uuid": metric.uuid, "has_error": False}, sort=[("start", pymongo.DESCENDING)]
    )
    return None if latest_successful is None else Measurement(metric, latest_successful)


def update_measurement_end(database: Database, measurement_id: MeasurementId):
    """Set the end date and time of the measurement to the current date and time."""
    return database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})
