"""Measurements collection."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

import pymongo
from pymongo.database import Database

from server_utilities.functions import iso_timestamp
from server_utilities.type import Addition, Direction, MeasurementId, MetricId, Scale, Status
from .datamodels import latest_datamodel


def latest_measurement(database: Database, metric_uuid: MetricId):
    """Return the latest measurement."""
    return database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])


def latest_successful_measurement(database: Database, metric_uuid: MetricId):
    """Return the latest successful measurement."""
    return database.measurements.find_one(
        filter={"metric_uuid": metric_uuid, "sources.value": {"$ne": None}}, sort=[("start", pymongo.DESCENDING)])


def recent_measurements_by_metric_uuid(database: Database, max_iso_timestamp: str, days=7):
    """Return all recent measurements."""
    min_iso_timestamp = (
        min([datetime.now(timezone.utc), datetime.fromisoformat(max_iso_timestamp)]) - timedelta(days=days)).isoformat()
    recent_measurements = database.measurements.find(
        filter={"end": {"$gt": min_iso_timestamp}, "start": {"$lt": max_iso_timestamp}},
        sort=[("start", pymongo.ASCENDING)], projection={"_id": False, "sources.entities": False})
    measurements_by_metric_uuid: Dict[MetricId, List] = {}
    for measurement in recent_measurements:
        measurements_by_metric_uuid.setdefault(measurement["metric_uuid"], []).append(measurement)
    return measurements_by_metric_uuid


def all_measurements(database: Database, metric_uuid: MetricId, max_iso_timestamp: str):
    """Return all measurements."""
    return database.measurements.find(filter={"metric_uuid": metric_uuid, "start": {"$lt": max_iso_timestamp}})


def count_measurements(database: Database) -> int:
    """Return the number of measurements."""
    return int(database.measurements.count_documents(filter={}))


def update_measurement_end(database: Database, measurement_id: MeasurementId):
    """Set the end date and time of the measurement to the current date and time."""
    return database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})


def insert_new_measurement(database: Database, metric: Dict, measurement: Dict) -> Dict:
    """Insert a new measurement."""
    if "_id" in measurement:
        del measurement["_id"]
    data_model = latest_datamodel(database)
    metric_type = data_model["metrics"][metric["type"]]
    metric_scale = metric.get("scale", "count")  # The current scale chosen by the user
    direction = metric.get("direction") or metric_type["direction"]
    for scale in metric_type["scales"]:
        value = calculate_measurement_value(measurement["sources"], metric["addition"], scale, direction)
        status = determine_measurement_status(database, metric, value)
        measurement[scale] = dict(value=value, status=status, direction=direction)
        for target in ("target", "near_target", "debt_target"):
            measurement[scale][target] = metric.get(target, metric_type.get(target)) if scale == metric_scale \
                else measurement.get(scale, {}).get(target)
    measurement["start"] = measurement["end"] = iso_timestamp()
    database.measurements.insert_one(measurement)
    del measurement["_id"]
    return measurement


def calculate_measurement_value(sources, addition: Addition, scale: Scale, direction: Direction) -> Optional[str]:
    """Calculate the measurement value from the source measurements."""

    def percentage(numerator: int, denominator: int) -> int:
        """Return the rounded percentage: numerator / denominator * 100%."""
        if denominator == 0:
            return 0 if direction == "<" else 100
        return int((100 * Decimal(numerator) / Decimal(denominator)).to_integral_value(ROUND_HALF_UP))

    def nr_entities_to_ignore(source) -> int:
        """Return the number of entities marked as fixed, false positive or won't fix."""
        entities = source.get("entity_user_data", {}).values()
        return len([entity for entity in entities if entity.get("status") in ("fixed", "false_positive", "wont_fix")])

    if not sources or any(source["parse_error"] or source["connection_error"] for source in sources):
        return None
    values = [int(source["value"]) - nr_entities_to_ignore(source) for source in sources]
    add = dict(max=max, min=min, sum=sum)[addition]
    if scale == "percentage":
        totals = [int(source["total"]) for source in sources]
        if addition == "sum":
            values, totals = [sum(values)], [sum(totals)]
        values = [percentage(value, total) for value, total in zip(values, totals)]
    return str(add(values))  # type: ignore


def determine_measurement_status(database: Database, metric, measurement_value: Optional[str]) -> Optional[Status]:
    """Determine the measurement status."""
    debt_end_date = metric.get("debt_end_date", date.max.isoformat())
    if measurement_value is None:
        return "debt_target_met" if metric["accept_debt"] and date.today().isoformat() <= debt_end_date else None
    direction = metric.get("direction") or latest_datamodel(database)["metrics"][metric["type"]]["direction"]
    value = int(measurement_value)
    target = int(metric.get("target") or 0)
    near_target = int(metric.get("near_target") or 0)
    debt_target = int(metric.get("debt_target") or 0)
    better_or_equal = {">": int.__ge__, "<": int.__le__}[direction]
    if better_or_equal(value, target):
        status: Status = "target_met"
    elif metric["accept_debt"] and date.today().isoformat() <= debt_end_date and better_or_equal(value, debt_target):
        status = "debt_target_met"
    elif better_or_equal(target, near_target) and better_or_equal(value, near_target):
        status = "near_target_met"
    else:
        status = "target_not_met"
    return status


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog for the measurements belonging the items with the specific uuids."""
    return database.measurements.find(
        filter={"delta.uuids": {"$in": list(uuids.values())}}, sort=[("start", pymongo.DESCENDING)],
        limit=nr_changes, projection=["delta", "start"])
