"""Measurements endpoint(s)."""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from initialization.database import quality_time_database
from database.measurements import (
    insert_new_measurement,
    latest_measurement,
    latest_successful_measurement,
    update_measurement_end,
)
from database.reports import latest_metric
from model.measurement import Measurement


router = APIRouter()


@router.post("/measurements")
async def post_measurements(
    measurement_data: dict, database: AsyncIOMotorDatabase = Depends(quality_time_database)
) -> None:
    """Add the measurement to the database, possibly merging it with an existing measurement if values are unchanged."""
    if (metric := await latest_metric(database, measurement_data["metric_uuid"])) is None:
        return  # Metric does not exist, must've been deleted while being measured
    latest = await latest_measurement(database, metric)
    measurement = Measurement(metric, measurement_data, previous_measurement=latest)
    if not measurement.sources_exist():
        return  # Measurement has sources that the metric does not have, must've been deleted while being measured
    if latest:
        latest_successful = await latest_successful_measurement(database, metric)
        measurement.copy_entity_user_data(latest if latest_successful is None else latest_successful)
        if measurement.equals(latest):
            # If the new measurement is equal to the previous one, merge them together
            await update_measurement_end(database, latest["_id"])
            return
    await insert_new_measurement(database, measurement)
