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


def insert_new_measurement(database: Database, metric_uuid: str, measurement, target: str = None,
                           debt_target: str = None, accept_debt: bool = None):
    """Insert a new measurement."""
    if "_id" in measurement:
        del measurement["_id"]
    metric = latest_metric(database, metric_uuid)
    measurement["value"] = calculate_measurement_value(measurement["sources"], metric["addition"])
    target = metric["target"] if target is None else target
    debt_target = metric["debt_target"] if debt_target is None else debt_target
    accept_debt = metric["accept_debt"] if accept_debt is None else accept_debt
    measurement["status"] = determine_measurement_status(
        database, metric, measurement["value"], target, debt_target, accept_debt)
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
        values.append(int(source["value"]) - len(source.get("ignored_units", [])))
    add = dict(sum=sum, max=max)[addition]
    return str(add(values))


def determine_measurement_status(
        database: Database, metric, measurement_value: Optional[str], metric_target: Optional[str],
        metric_debt_target: Optional[str], metric_accept_debt: Optional[bool]) -> Optional[str]:
    """Determine the measurement status."""
    if measurement_value is None:
        return None
    datamodel = latest_datamodel(database)
    direction = datamodel["metrics"][metric["type"]]["direction"]
    value = int(measurement_value)
    target = int(metric_target or metric["target"])
    debt_target = int(metric_debt_target or metric["debt_target"] or target)
    better_or_equal = {">=": int.__ge__, "<=": int.__le__, "==": int.__eq__}[direction]
    if better_or_equal(value, target):
        status = "target_met"
    elif metric_accept_debt and better_or_equal(value, debt_target):
        status = "debt_target_met"
    else:
        status = "target_not_met"
    return status
