"""Measurements collection."""

import pymongo
from pymongo.database import Database

from shared.model.measurement import Measurement
from shared.model.metric import Metric


def latest_successful_measurement(database: Database, metric: Metric) -> Measurement | None:
    """Return the latest successful measurement."""
    latest_successful = database.measurements.find_one(
        {"metric_uuid": metric.uuid, "has_error": False}, sort=[("start", pymongo.DESCENDING)]
    )
    return None if latest_successful is None else Measurement(metric, latest_successful)
