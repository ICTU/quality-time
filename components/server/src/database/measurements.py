"""Measurements collection."""

from datetime import datetime, timedelta
from typing import Optional

import pymongo
from pymongo.database import Database

from model.measurement import Measurement
from model.metric import Metric
from server_utilities.functions import iso_timestamp
from server_utilities.type import MetricId


def latest_measurement(database: Database, metric: Metric) -> Optional[Measurement]:
    """Return the latest measurement."""
    latest = database.measurements.find_one(filter={"metric_uuid": metric.uuid}, sort=[("start", pymongo.DESCENDING)])
    return None if latest is None else Measurement(metric, latest)


def recent_measurements_by_metric_uuid(database: Database, max_iso_timestamp: str = "", days=7):
    """Return all recent measurements."""
    max_iso_timestamp = max_iso_timestamp or iso_timestamp()
    min_iso_timestamp = (datetime.fromisoformat(max_iso_timestamp) - timedelta(days=days)).isoformat()
    recent_measurements = database.measurements.find(
        filter={"end": {"$gte": min_iso_timestamp}, "start": {"$lte": max_iso_timestamp}},
        sort=[("start", pymongo.ASCENDING)],
        projection={"_id": False, "sources.entities": False},
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
        measurement_filter, projection={"_id": False, "sources.entities": False, "issue_status": False}
    )
    return list(all_measurements_stripped)[:-1] + [latest_measurement_complete]


def count_measurements(database: Database) -> int:
    """Return the number of measurements."""
    return int(database.measurements.estimated_document_count())


def insert_new_measurement(database: Database, measurement: Measurement) -> Measurement:
    """Insert a new measurement."""
    measurement.update_measurement()
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
