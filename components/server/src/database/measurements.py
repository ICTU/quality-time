"""Measurements collection."""

from datetime import date
from typing import Optional

import pymongo
from pymongo.database import Database
from shared.utilities.functions import iso_timestamp

from .datamodels import latest_datamodel
from .reports import latest_metric


def latest_measurement(database: Database, metric_uuid: str):
    """Return the latest measurement."""
    return database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])


def last_measurements(database: Database, report_uuid: str):
    """Return the last measurement for each metric."""
    return database.measurements.find(filter={"report_uuid": report_uuid, "last": True})


def recent_measurements(database: Database, metric_uuid: str, max_iso_timestamp: str):
    """Return the recent measurements."""
    return database.measurements.find(filter={"metric_uuid": metric_uuid, "start": {"$lt": max_iso_timestamp}})


def count_measurements(database: Database, report_uuid: str) -> int:
    """Return the number of measurements."""
    return database.measurements.count_documents(filter={"report_uuid": report_uuid})


def insert_new_measurement(database: Database, measurement, metric=None):
    """Insert a new measurement."""
    measurement.pop("_id", None)
    metric = latest_metric(
        database, measurement["report_uuid"], measurement["metric_uuid"]) if metric is None else metric
    measurement["value"] = calculate_measurement_value(measurement["sources"], metric["addition"])
    measurement["status"] = determine_measurement_status(database, metric, measurement["value"])
    measurement["start"] = measurement["end"] = iso_timestamp()
    # Mark this measurement as the most recent one:
    measurement["last"] = True
    # And unset the last flag on the previous measurement(s):
    database.measurements.update_many(
        filter={"metric_uuid": measurement["metric_uuid"], "last": True}, update={"$unset": {"last": ""}})
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
        entities_to_ignore = [
            entity for entity in source.get("entity_user_data", {}).values()
            if entity.get("status") in ("fixed", "false_positive", "wont_fix")]
        values.append(int(source["value"]) - len(entities_to_ignore))
    add = dict(max=max, min=min, sum=sum)[addition]
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
    debt_end_date = metric.get("debt_end_date", date.max.isoformat())
    better_or_equal = {"≧": int.__ge__, "≦": int.__le__, "=": int.__eq__}[direction]
    if better_or_equal(value, target):
        status = "target_met"
    elif metric["accept_debt"] and date.today().isoformat() <= debt_end_date and better_or_equal(value, debt_target):
        status = "debt_target_met"
    elif better_or_equal(target, near_target) and better_or_equal(value, near_target):
        status = "near_target_met"
    else:
        status = "target_not_met"
    return status
