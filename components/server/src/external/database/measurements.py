"""Measurements collection."""

from datetime import datetime, timedelta
from typing import Any

import pymongo
from pymongo.database import Database

from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.utils.functions import iso_timestamp
from shared.utils.type import MetricId


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog for the measurements belonging to the items with the specific uuids."""
    return database.measurements.find(
        filter={"delta.uuids": {"$in": list(uuids.values())}},
        sort=[("start", pymongo.DESCENDING)],
        limit=nr_changes,
        projection=["delta", "start"],
    )


def count_measurements(database: Database) -> int:
    """Return the number of measurements."""
    return int(database.measurements.estimated_document_count())


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
