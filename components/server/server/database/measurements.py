"""Measurements collection."""

from typing import Optional

import pymongo

from ..util import iso_timestamp
from .datamodels import latest_datamodel
from .reports import latest_metric


def latest_measurement(metric_uuid: str, database):
    """Return the latest measurement."""
    return database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])


def latest_measurements(metric_uuid: str, max_iso_timestamp: str, database):
    """Return the latest measurements."""
    return database.measurements.find(filter={"metric_uuid": metric_uuid, "start": {"$lt": max_iso_timestamp}})


def count_measurements(report_uuid: str, database) -> int:
    """Return the number of measurements."""
    return database.measurements.count_documents(filter={"report_uuid": report_uuid})


def insert_new_measurement(metric_uuid: str, measurement, database, target: str = None):
    """Insert a new measurement."""
    if "_id" in measurement:
        del measurement["_id"]
    measurement["value"] = calculate_measurement_value(measurement["sources"])
    target = target or latest_metric(metric_uuid, iso_timestamp(), database)["target"]
    measurement["status"] = determine_measurement_status(metric_uuid, measurement["value"], target, database)
    measurement["start"] = measurement["end"] = iso_timestamp()
    database.measurements.insert_one(measurement)
    measurement["_id"] = str(measurement["_id"])
    return measurement


def calculate_measurement_value(sources) -> Optional[str]:
    """Calculate the measurement value from the source measurements."""
    value = 0
    for source in sources:
        if source["parse_error"] or source["connection_error"]:
            return None
        value += (int(source["value"]) - len(source.get("ignored_units", [])))
    return str(value)


def determine_measurement_status(metric_uuid: str, measurement_value: Optional[str], metric_target: Optional[str],
                                 database) -> Optional[str]:
    """Determine the measurement status."""
    if measurement_value is None:
        return None
    metric = latest_metric(metric_uuid, iso_timestamp(), database)
    datamodel = latest_datamodel(iso_timestamp(), database)
    direction = datamodel["metrics"][metric["type"]]["direction"]
    value = int(measurement_value)
    target = int(metric_target or metric["target"])
    if direction == ">=":
        status = "target_met" if value >= target else "target_not_met"
    elif direction == "<=":
        status = "target_met" if value <= target else "target_not_met"
    else:
        status = "target_met" if value == target else "target_not_met"
    return status
