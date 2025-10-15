"""Measurements collection."""

from datetime import datetime, timedelta
from typing import Any, TYPE_CHECKING

import pymongo

from shared.model.measurement import Measurement
from shared.utils.functions import iso_timestamp

if TYPE_CHECKING:
    from pymongo.database import Database

    from shared.model.metric import Metric
    from shared.utils.type import MetricId


# Projection options
NO_ID = {"_id": False}
NO_SOURCE_DETAILS = NO_ID | {"sources.entities": False}
NO_MEASUREMENT_DETAILS = NO_SOURCE_DETAILS | {"issue_status": False}

# Sort optins
START_ASCENDING = [("start", pymongo.ASCENDING), ("end", pymongo.DESCENDING)]
START_DESCENDING = [("start", pymongo.DESCENDING)]


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog for the measurements belonging to the items with the specific uuids."""
    return database.measurements.find(
        filter={"delta.uuids": {"$in": list(uuids.values())}},
        sort=START_DESCENDING,
        limit=nr_changes,
        projection=["delta", "start"],
    )


def count_measurements(database: Database) -> int:
    """Return the number of measurements."""
    return int(database.measurements.estimated_document_count())


def measurements_in_period(database: Database, min_iso_timestamp: str, max_iso_timestamp: str):
    """Return recent measurements within the specified period, without source details and issue status."""
    # Return measurements that partially or completely overlap with the period, meaning they have their start before
    # the end of the period (max_iso_timestamp) and their end after the start of the period (min_iso_timestamp):
    now = iso_timestamp()
    measurement_filter = {"start": {"$lte": max_iso_timestamp or now}, "end": {"$gte": min_iso_timestamp or now}}
    return list(database.measurements.find(measurement_filter, sort=START_ASCENDING, projection=NO_MEASUREMENT_DETAILS))


def all_metric_measurements(database: Database, metric_uuid: MetricId, max_iso_timestamp: str):
    """Return all measurements for one metric, without entities and issue status, except for the most recent one."""
    measurement_filter: dict[str, str | dict[str, str]] = {"metric_uuid": str(metric_uuid)}
    if max_iso_timestamp:
        measurement_filter["start"] = {"$lte": max_iso_timestamp}
    latest_measurement = database.measurements.find_one(measurement_filter, sort=START_DESCENDING, projection=NO_ID)
    if not latest_measurement:
        return []
    all_measurements_stripped = list(
        database.measurements.find(measurement_filter, sort=START_ASCENDING, projection=NO_MEASUREMENT_DETAILS),
    )
    return [*all_measurements_stripped[:-1], latest_measurement]


def recent_measurements(
    database: Database,
    metrics_dict: dict[MetricId, Metric],
    max_iso_timestamp: str = "",
    days: int = 7,
) -> dict[MetricId, list[Measurement]]:
    """Return all recent measurements."""
    max_iso_timestamp = max_iso_timestamp or iso_timestamp()
    min_iso_timestamp = (datetime.fromisoformat(max_iso_timestamp) - timedelta(days=days)).isoformat()
    measurement_filter: dict[str, Any] = {"start": {"$lte": max_iso_timestamp}, "end": {"$gte": min_iso_timestamp}}
    measurements = database.measurements.find(measurement_filter, sort=START_ASCENDING, projection=NO_SOURCE_DETAILS)
    measurements_by_metric_uuid: dict[MetricId, list] = {}
    for measurement_dict in measurements:
        metric_uuid = measurement_dict["metric_uuid"]
        # Only process the measurement if its metric exists:
        if metric := metrics_dict.get(metric_uuid):  # pragma: no feature-test-cover
            measurement = Measurement(metric, measurement_dict)
            measurements_by_metric_uuid.setdefault(metric_uuid, []).append(measurement)
    return measurements_by_metric_uuid
