"""Measurements collection."""

from datetime import datetime, timedelta
from typing import Any, NewType

import pymongo
from pymongo.database import Database

from shared.initialization.database import database_connection
from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.utils.functions import iso_timestamp
from shared.utils.type import MetricId

MeasurementId = NewType("MeasurementId", str)


def latest_successful_measurement(metric: Metric) -> Measurement | None:
    """Return the latest successful measurement."""
    database_pointer = database_connection()
    latest_successful = database_pointer.measurements.find_one(
        {"metric_uuid": metric.uuid, "has_error": False}, sort=[("start", pymongo.DESCENDING)]
    )
    return None if latest_successful is None else Measurement(metric, latest_successful)


def update_measurement_end(measurement_id: MeasurementId):
    """Set the end date and time of the measurement to the current date and time."""
    database_pointer = database_connection()
    return database_pointer.measurements.update_one(
        filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}}
    )


def get_recent_measurements(metrics: list[Metric], limit_per_metric: int = 2) -> list[Measurement]:
    """Return recent measurements for the specified metrics, without entities and issue status."""
    database_pointer = database_connection()
    projection = {
        "_id": False,
        "sources.entities": False,
        "sources.entity_user_data": False,
        "issue_status": False,
    }
    measurements: list = []
    for metric in metrics:
        measurement_data = list(
            database_pointer["measurements"].find(
                {"metric_uuid": metric.uuid},
                limit=limit_per_metric,
                sort=[("start", pymongo.DESCENDING)],
                projection=projection,
            )
        )
        for measurement in measurement_data:
            measurements.append(Measurement(metric, measurement))

    return measurements


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


def recent_measurements(
    database: Database, metrics_dict: dict[MetricId, Metric], max_iso_timestamp: str = "", days: int = 7
) -> dict[MetricId, list[Measurement]]:
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
