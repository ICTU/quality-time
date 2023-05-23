"""Measurements collection."""

import pymongo
from pymongo.database import Database

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
    """Return recent measurements for the specified metrics, without entities and issue status."""
    if not metric_uuids:
        return []
    measurement_filter: dict = {"metric_uuid": {"$in": metric_uuids}}
    if min_iso_timestamp:  # pragma: no feature-test-cover
        measurement_filter["end"] = {"$gt": min_iso_timestamp}
    if max_iso_timestamp:  # pragma: no feature-test-cover
        measurement_filter["start"] = {"$lt": max_iso_timestamp}
    return list(
        database.measurements.find(
            measurement_filter,
            sort=[("start", pymongo.ASCENDING)],
            projection={
                "_id": False,
                "sources.entities": False,
                "sources.entity_user_data": False,
                "issue_status": False,
            },
        ),
    )


def all_metric_measurements(
    database: Database,
    metric_uuid: MetricId,
    max_iso_timestamp: str = "",
):
    """Return all measurements for one metric, without entities and issue status, except for the most recent one."""
    measurement_filter: dict = {"metric_uuid": metric_uuid}
    if max_iso_timestamp:
        measurement_filter["start"] = {"$lt": max_iso_timestamp}
    latest_measurement_complete = database.measurements.find_one(
        measurement_filter,
        sort=[("start", pymongo.DESCENDING)],
        projection={"_id": False},
    )
    if not latest_measurement_complete:
        return []
    all_measurements_stripped = measurements_by_metric(database, metric_uuid, max_iso_timestamp=max_iso_timestamp)
    return list(all_measurements_stripped)[:-1] + [latest_measurement_complete]
