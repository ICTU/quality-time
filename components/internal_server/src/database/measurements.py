"""Measurements collection."""

import pymongo
from pymongo.database import Database

from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.utils.functions import iso_timestamp

from utils.type import MeasurementId


def latest_successful_measurement(database: Database, metric: Metric) -> Measurement | None:
    """Return the latest successful measurement."""
    latest_successful = database.measurements.find_one(
        {"metric_uuid": metric.uuid, "has_error": False}, sort=[("start", pymongo.DESCENDING)]
    )
    return None if latest_successful is None else Measurement(metric, latest_successful)


def update_measurement_end(database: Database, measurement_id: MeasurementId):
    """Set the end date and time of the measurement to the current date and time."""
    return database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})


def recent_measurements(database: Database, *metrics: Metric, limit_per_metric: int = 2):
    """Return recent measurements for the specified metrics, without entities and issue status."""
    projection = {
        "_id": False,
        "sources.entities": False,
        "sources.entity_user_data": False,
        "issue_status": False,
    }
    measurements: list = []
    for metric in metrics:
        measurements.extend(
            list(
                database.measurements.find(
                    {"metric_uuid": metric.uuid},
                    limit=limit_per_metric,
                    sort=[("start", pymongo.DESCENDING)],
                    projection=projection,
                )
            )
        )
    return measurements
