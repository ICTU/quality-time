"""Measurements collection."""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional, Union

import pymongo
from pymongo.database import Database

from server_utilities.functions import iso_timestamp
from server_utilities.type import Addition, Direction, MeasurementId, MetricId, ReportId, Scale, Status
from .datamodels import latest_datamodel


def latest_measurement(database: Database, metric_uuid: MetricId):
    """Return the latest measurement."""
    return database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])


def last_measurements(database: Database, report_uuid: ReportId):
    """Return the last measurement for each metric."""
    measurement_filter: Dict[str, Union[bool, str]] = dict(last=True)
    if not report_uuid.startswith("tag-"):
        measurement_filter["report_uuid"] = report_uuid
    return database.measurements.find(filter=measurement_filter)


def recent_measurements(database: Database, metric_uuid: MetricId, max_iso_timestamp: str):
    """Return the recent measurements."""
    return database.measurements.find(filter={"metric_uuid": metric_uuid, "start": {"$lt": max_iso_timestamp}})


def count_measurements(database: Database, report_uuid: ReportId) -> int:
    """Return the number of measurements."""
    return int(database.measurements.count_documents(filter={"report_uuid": report_uuid}))


def update_measurement_end(database: Database, measurement_id: MeasurementId):
    """Set the end date and time of the measurement to the current date and time."""
    # Setting last to true shouldn't be necessary in the long run because the last flag is set to true when a new
    # measurement is added. However, setting it here ensures the measurement collection is updated correctly after the
    # release of this code. This (setting last to true) was added in the version immediately after v0.5.1.
    return database.measurements.update_one(
        filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp(), "last": True}})


def insert_new_measurement(database: Database, metric: Dict, measurement: Dict) -> Dict:
    """Insert a new measurement."""
    if "_id" in measurement:
        del measurement["_id"]
    data_model = latest_datamodel(database)
    metric_type = data_model["metrics"][metric["type"]]
    direction = metric.get("direction") or metric_type["direction"]
    for scale in metric_type["scales"]:
        value = calculate_measurement_value(measurement["sources"], metric["addition"], scale, direction)
        status = determine_measurement_status(database, metric, value)
        measurement[scale] = dict(value=value, status=status)
    measurement["start"] = measurement["end"] = iso_timestamp()
    # Mark this measurement as the most recent one:
    measurement["last"] = True
    # And unset the last flag on the previous measurement(s):
    database.measurements.update_many(
        filter={"metric_uuid": measurement["metric_uuid"], "last": True}, update={"$unset": {"last": ""}})
    database.measurements.insert_one(measurement)
    measurement["_id"] = str(measurement["_id"])
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
    if measurement_value is None:
        return None
    direction = metric.get("direction") or latest_datamodel(database)["metrics"][metric["type"]]["direction"]
    value = int(measurement_value)
    target = int(metric["target"])
    near_target = int(metric["near_target"])
    debt_target = int(metric["debt_target"] or target)
    debt_end_date = metric.get("debt_end_date", date.max.isoformat())
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


def changelog(database: Database, report_uuid: ReportId, nr_changes: int):
    """Return the changelog for the measurements in the report."""
    return database.measurements.find(
        filter={"report_uuid": report_uuid, "delta": {"$exists": True}}, sort=[("start", pymongo.DESCENDING)],
        limit=nr_changes, projection=["delta", "start"])
