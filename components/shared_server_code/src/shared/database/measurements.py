"""Measurements collection."""

from datetime import datetime, timedelta
from typing import Any

import pymongo
from pymongo.database import Database

from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.utils.functions import iso_timestamp
from shared.utils.type import MetricId


def latest_measurement(database: Database, metric: Metric) -> Measurement | None:
    """Return the latest measurement."""
    latest = database.measurements.find_one(filter={"metric_uuid": metric.uuid}, sort=[("start", pymongo.DESCENDING)])
    return None if latest is None else Measurement(metric, latest)


def insert_new_measurement(database: Database, measurement: Measurement) -> Measurement:
    """Insert a new measurement."""
    measurement.update_measurement()
    if "_id" in measurement:
        del measurement["_id"]  # Remove the Mongo ID if present so this measurement can be re-inserted in the database.
    database.measurements.insert_one(measurement)
    del measurement["_id"]
    return measurement


def recent_measurements(database: Database, metrics_dict: dict[str, Metric], max_iso_timestamp: str = "", days=7):
    """Return all recent measurements, or only those of the specified metrics."""
    max_iso_timestamp = max_iso_timestamp or iso_timestamp()
    min_iso_timestamp = (datetime.fromisoformat(max_iso_timestamp) - timedelta(days=days)).isoformat()
    measurement_filter: dict[str, Any] = {"end": {"$gte": min_iso_timestamp}, "start": {"$lte": max_iso_timestamp}}
    measurement_filter["metric_uuid"] = {"$in": list(metrics_dict.keys())}
    projection = {"_id": False, "sources.entities": False, "entity_user_data": False}
    measurements = database.measurements.find(
        measurement_filter,
        sort=[("start", pymongo.ASCENDING)],
        projection=projection,
    )
    measurements_by_metric_uuid: dict[MetricId, list] = {}
    for measurement_dict in measurements:
        metric_uuid = measurement_dict["metric_uuid"]
        metric = metrics_dict[metric_uuid]
        measurement = Measurement(metric, measurement_dict)
        measurements_by_metric_uuid.setdefault(metric_uuid, []).append(measurement)
    return measurements_by_metric_uuid
