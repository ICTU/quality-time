"""Measurements collection."""

from datetime import datetime, timedelta

import pymongo
from pymongo.database import Database

from model.measurement import Measurement
from model.metric import Metric
from server_utilities.functions import iso_timestamp
from server_utilities.type import MeasurementId, MetricId


def latest_measurement(database: Database, metric: Metric) -> Measurement | None:
    """Return the latest measurement."""
    latest = database.measurements.find_one(filter={"metric_uuid": metric.uuid}, sort=[("start", pymongo.DESCENDING)])
    return None if latest is None else Measurement(metric, latest)


def latest_measurements_by_metric_uuid(database: Database, metric_uuids: list[str]) -> dict[str, Measurement] | None:
    """Return the latest measurements in a dict with metric_uuids as keys."""
    latest_measurement_ids = database.measurements.aggregate(
        [
            {"$match": {"metric_uuid": {"$in": metric_uuids}}},
            {"$sort": {"metric_uuid": 1, "start": -1}},
            {"$group": {"_id": "$metric_uuid", "measurement_id": {"$first": "$_id"}}},
            {"$project": {"_id": False}},
        ]
    )
    latest_measurements = database.measurements.find(
        {"_id": {"$in": [measurement["measurement_id"] for measurement in latest_measurement_ids]}},
        projection={"_id": False, "sources.entities": False, "entity_user_data": False},
    )
    return {measurement["metric_uuid"]: measurement for measurement in latest_measurements}


def latest_successful_measurement(database: Database, metric: Metric) -> Measurement | None:
    """Return the latest successful measurement."""
    latest_successful = database.measurements.find_one(
        {"metric_uuid": metric.uuid, "has_error": False}, sort=[("start", pymongo.DESCENDING)]
    )
    return None if latest_successful is None else Measurement(metric, latest_successful)


def recent_measurements_by_metric_uuid(database: Database, max_iso_timestamp: str = "", days=7, metric_uuids=None):
    """Return all recent measurements, or only those of the specified metrics."""
    max_iso_timestamp = max_iso_timestamp or iso_timestamp()
    min_iso_timestamp = (datetime.fromisoformat(max_iso_timestamp) - timedelta(days=days)).isoformat()
    measurement_filter = {"end": {"$gte": min_iso_timestamp}, "start": {"$lte": max_iso_timestamp}}
    # metric_uuids needs to be optional as long as the /reports endpoint is supported for backwards compatibility
    # however, there is no test anymore covering that endpoint, which means incomplete coverage on this if statement
    if metric_uuids is not None:  # pragma: no cover
        measurement_filter["metric_uuid"] = {"$in": metric_uuids}
    recent_measurements = database.measurements.find(
        measurement_filter,
        sort=[("start", pymongo.ASCENDING)],
        projection={"_id": False, "metric_uuid": True, "start": True, "end": True, "value": True},
    )
    measurements_by_metric_uuid: dict[MetricId, list] = {}
    for measurement in recent_measurements:
        measurements_by_metric_uuid.setdefault(measurement["metric_uuid"], []).append(measurement)
    return measurements_by_metric_uuid


def measurements_by_metric(
    database: Database,
    *metric_uuids: MetricId,
    min_iso_timestamp: str = "",
    max_iso_timestamp: str = "",
):
    """Return all measurements for one metric, without entities and issue status, except for the most recent one."""
    measurement_filter: dict = {"metric_uuid": {"$in": metric_uuids}}
    if min_iso_timestamp:
        measurement_filter["end"] = {"$gt": min_iso_timestamp}
    if max_iso_timestamp:
        measurement_filter["start"] = {"$lt": max_iso_timestamp}
    latest_measurement_complete = database.measurements.find_one(
        measurement_filter, sort=[("start", pymongo.DESCENDING)], projection={"_id": False}
    )
    if not latest_measurement_complete:
        return []
    all_measurements_stripped = database.measurements.find(
        measurement_filter,
        projection={"_id": False, "sources.entities": False, "sources.entity_user_data": False, "issue_status": False},
    )
    return list(all_measurements_stripped)[:-1] + [latest_measurement_complete]


def count_measurements(database: Database) -> int:
    """Return the number of measurements."""
    return int(database.measurements.estimated_document_count())


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


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog for the measurements belonging to the items with the specific uuids."""
    return database.measurements.find(
        filter={"delta.uuids": {"$in": list(uuids.values())}},
        sort=[("start", pymongo.DESCENDING)],
        limit=nr_changes,
        projection=["delta", "start"],
    )
