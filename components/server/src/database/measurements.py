"""Measurements collection."""

from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Optional

import pymongo
from pymongo.database import Database

from model.measurement import Measurement, Source
from model.metric import Metric
from server_utilities.functions import iso_timestamp, percentage
from server_utilities.type import MeasurementId, MetricId, Scale


def latest_measurement(database: Database, metric_uuid: MetricId, metric: Metric) -> Optional[Measurement]:
    """Return the latest measurement."""
    latest = database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])
    return None if latest is None else Measurement(metric, latest)


def latest_successful_measurement(database: Database, metric_uuid: MetricId, metric: Metric) -> Optional[Measurement]:
    """Return the latest successful measurement."""
    latest_successful = database.measurements.find_one(
        filter={"metric_uuid": metric_uuid, "sources.value": {"$ne": None}}, sort=[("start", pymongo.DESCENDING)]
    )
    return None if latest_successful is None else Measurement(metric, latest_successful)


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
    """Return all measurements for one metric, without the entities, except for the most recent one."""
    measurement_filter: dict = {"metric_uuid": {"$in": metric_uuids}}
    if min_iso_timestamp:
        measurement_filter["end"] = {"$gt": min_iso_timestamp}
    if max_iso_timestamp:
        measurement_filter["start"] = {"$lt": max_iso_timestamp}
    latest_with_entities = database.measurements.find_one(
        measurement_filter, sort=[("start", pymongo.DESCENDING)], projection={"_id": False}
    )
    if not latest_with_entities:
        return []
    all_measurements_without_entities = database.measurements.find(
        measurement_filter, projection={"_id": False, "sources.entities": False}
    )
    return list(all_measurements_without_entities)[:-1] + [latest_with_entities]


def count_measurements(database: Database) -> int:
    """Return the number of measurements."""
    return int(database.measurements.count_documents(filter={}))


def update_measurement_end(database: Database, measurement_id: MeasurementId):
    """Set the end date and time of the measurement to the current date and time."""
    return database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})


def insert_new_measurement(
    database: Database, metric: Metric, measurement: Measurement, previous_measurement: Measurement
) -> dict:
    """Insert a new measurement."""
    for scale in metric.scales():
        value = calculate_measurement_value(metric, measurement.sources(), scale)
        status = metric.status(value)
        measurement[scale] = dict(value=value, direction=metric.direction())
        measurement.set_status(scale, status, previous_measurement)
        if scale == metric.scale():
            measurement.set_target(scale, "target", metric.get_target("target"))
            measurement.set_target(scale, "near_target", metric.get_target("near_target"))
            target_value = None if metric.accept_debt_expired() else metric.get_target("debt_target")
            measurement.set_target(scale, "debt_target", target_value)
    if "_id" in measurement:
        del measurement["_id"]  # Remove the Mongo ID if present so this measurement can be re-inserted in the database.
    database.measurements.insert_one(measurement)
    del measurement["_id"]
    return measurement


def calculate_measurement_value(metric: Metric, sources: Sequence[Source], scale: Scale) -> Optional[str]:
    """Calculate the measurement value from the source measurements."""
    if not sources or any(source["parse_error"] or source["connection_error"] for source in sources):
        return None
    values = [source.value() for source in sources]
    add = metric.addition()
    if scale == "percentage":
        direction = metric.direction()
        totals = [source.total() for source in sources]
        if add is sum:
            values, totals = [sum(values)], [sum(totals)]
        values = [percentage(value, total, direction) for value, total in zip(values, totals)]
    return str(add(values))


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog for the measurements belonging to the items with the specific uuids."""
    return database.measurements.find(
        filter={"delta.uuids": {"$in": list(uuids.values())}},
        sort=[("start", pymongo.DESCENDING)],
        limit=nr_changes,
        projection=["delta", "start"],
    )
