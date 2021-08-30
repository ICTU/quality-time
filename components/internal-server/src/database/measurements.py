"""Measurements collection."""

from typing import Optional

import pymongo
from motor.motor_asyncio import AsyncIOMotorDatabase

from model.measurement import Measurement
from model.metric import Metric
from utilities.functions import iso_timestamp
from utilities.type import MeasurementId


async def latest_measurement(database: AsyncIOMotorDatabase, metric: Metric) -> Optional[Measurement]:
    """Return the latest measurement."""
    latest = await database.measurements.find_one(
        filter={"metric_uuid": metric.uuid}, sort=[("start", pymongo.DESCENDING)]
    )
    return None if latest is None else Measurement(metric, latest)


async def latest_successful_measurement(database: AsyncIOMotorDatabase, metric: Metric) -> Optional[Measurement]:
    """Return the latest successful measurement."""
    latest_successful = await database.measurements.find_one(
        filter={"metric_uuid": metric.uuid, "has_error": False}, sort=[("start", pymongo.DESCENDING)]
    )
    return None if latest_successful is None else Measurement(metric, latest_successful)


async def update_measurement_end(database: AsyncIOMotorDatabase, measurement_id: MeasurementId):
    """Set the end date and time of the measurement to the current date and time."""
    await database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})


async def insert_new_measurement(database: AsyncIOMotorDatabase, measurement: Measurement) -> Measurement:
    """Insert a new measurement into the measurements collection."""
    measurement.update_measurement()
    if "_id" in measurement:
        del measurement["_id"]  # Remove the Mongo ID if present so this measurement can be re-inserted in the database.
    await database.measurements.insert_one(measurement)
    del measurement["_id"]
    return measurement
