"""Measurements collection."""

from datetime import datetime, timedelta
from typing import Any, Union

import pymongo
from pymongo.database import Database

from external.model.measurement import Measurement
from external.model.metric import Metric
from external.server_utilities.functions import iso_timestamp
from external.server_utilities.type import MetricId


def latest_measurement(database: Database, metric: Metric) -> Measurement | None:
    """Return the latest measurement."""
    latest = database.measurements.find_one(filter={"metric_uuid": metric.uuid}, sort=[("start", pymongo.DESCENDING)])
    return None if latest is None else Measurement(metric, latest)


MatchType = dict[str, dict[str, Union[list[str], str]]]


def latest_measurements_by_metric_uuid(
    database: Database, date_time: str, metric_uuids: list[str]
) -> dict[str, Measurement] | None:
    """Return the latest measurements in a dict with metric_uuids as keys."""
    metric_uuid_match: MatchType = {"metric_uuid": {"$in": metric_uuids}}
    date_time_match: MatchType = {"start": {"$lte": date_time}} if date_time else {}
    latest_measurement_ids = database.measurements.aggregate(
        [
            {"$match": metric_uuid_match | date_time_match},  # skipcq: TYP-052
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


def recent_measurements_by_metric_uuid(
    data_model: dict, database: Database, max_iso_timestamp: str = "", days=7, metric_uuids=None
):
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
