"""Measurement routes."""

import bottle
from pymongo.database import Database

from database.measurements import (
    insert_new_measurement,
    latest_measurement,
    update_measurement_end,
)
from model.measurement import Measurement

from ..database.measurements import latest_successful_measurement
from ..database.reports import latest_metric


@bottle.post("/internal-api/v3/measurements", authentication_required=False)
def post_measurement(database: Database) -> None:
    """Put the measurement in the database."""
    measurement_data = dict(bottle.request.json)
    metric_uuid = measurement_data["metric_uuid"]
    if (metric := latest_metric(database, metric_uuid)) is None:
        return  # Metric does not exist, must've been deleted while being measured
    latest = latest_measurement(database, metric)
    measurement = Measurement(metric, measurement_data, previous_measurement=latest)
    if not measurement.sources_exist():
        return  # Measurement has sources that the metric does not have, must've been deleted while being measured
    if latest:
        latest_successful = latest_successful_measurement(database, metric)
        measurement.copy_entity_user_data(latest if latest_successful is None else latest_successful)
        if measurement.equals(latest):
            # If the new measurement is equal to the previous one, merge them together
            update_measurement_end(database, latest["_id"])
            return
    insert_new_measurement(database, measurement)
