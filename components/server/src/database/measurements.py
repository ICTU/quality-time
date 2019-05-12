"""Measurements collection."""

from typing import Optional

import pymongo
from pymongo.database import Database

from ..util import iso_timestamp
from .datamodels import latest_datamodel
from .reports import latest_metric


def latest_measurement(database: Database, metric_uuid: str):
    """Return the latest measurement."""
    return database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])


def latest_measurements(database: Database, metric_uuid: str, max_iso_timestamp: str):
    """Return the latest measurements."""
    return database.measurements.find(filter={"metric_uuid": metric_uuid, "start": {"$lt": max_iso_timestamp}})


def count_measurements(database: Database, report_uuid: str) -> int:
    """Return the number of measurements."""
    return database.measurements.count_documents(filter={"report_uuid": report_uuid})


def update_measurement_end(database: Database, measurement_id: str):
    """Set the end date and time of the measurement to the current date and time."""
    return database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})


def insert_new_measurement(database: Database, measurement, metric=None):
    """Insert a new measurement."""
    if "_id" in measurement:
        del measurement["_id"]
    metric = latest_metric(database, measurement["metric_uuid"]) if metric is None else metric
    measurement["value"] = calculate_measurement_value(measurement["sources"], metric["addition"])
    measurement["status"] = determine_measurement_status(database, metric, measurement["value"])
    measurement["start"] = measurement["end"] = iso_timestamp()
    database.measurements.insert_one(measurement)
    measurement["_id"] = str(measurement["_id"])
    return measurement


def calculate_measurement_value(sources, addition: str) -> Optional[str]:
    """Calculate the measurement value from the source measurements."""
    if not sources:
        return None
    values = []
    for source in sources:
        if source["parse_error"] or source["connection_error"]:
            return None
        statuses = source.get("unit_attributes", {}).get("status", {}).items()
        units_to_ignore = {
            unit_key: status for unit_key, status in statuses if status in ("wont_fix", "false_positive", "fixed")}
        values.append(int(source["value"]) - len(units_to_ignore))
    add = dict(sum=sum, max=max)[addition]
    return str(add(values))  # type: ignore


def determine_measurement_status(database: Database, metric, measurement_value: Optional[str]) -> Optional[str]:
    """Determine the measurement status."""
    if measurement_value is None:
        return None
    datamodel = latest_datamodel(database)
    direction = datamodel["metrics"][metric["type"]]["direction"]
    value = int(measurement_value)
    target = int(metric["target"])
    near_target = int(metric["near_target"])
    debt_target = int(metric["debt_target"] or target)
    better_or_equal = {">=": int.__ge__, "<=": int.__le__, "==": int.__eq__}[direction]
    if better_or_equal(value, target):
        status = "target_met"
    elif metric["accept_debt"] and better_or_equal(value, debt_target):
        status = "debt_target_met"
    elif better_or_equal(target, near_target) and better_or_equal(value, near_target):
        status = "near_target_met"
    else:
        status = "target_not_met"
    return status
