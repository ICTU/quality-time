"""Measurements collection."""

from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Literal, Optional, Union, cast

import pymongo
from pymongo.database import Database

from model.queries import get_attribute_type, get_measured_attribute
from server_utilities.functions import iso_timestamp
from server_utilities.type import Direction, MeasurementId, MetricId, Scale, Status

TargetType = Literal["target", "near_target", "debt_target"]


def latest_measurement(database: Database, metric_uuid: MetricId):
    """Return the latest measurement."""
    return database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])


def latest_successful_measurement(database: Database, metric_uuid: MetricId):
    """Return the latest successful measurement."""
    return database.measurements.find_one(
        filter={"metric_uuid": metric_uuid, "sources.value": {"$ne": None}}, sort=[("start", pymongo.DESCENDING)])


def recent_measurements_by_metric_uuid(database: Database, max_iso_timestamp: str = "", days=7):
    """Return all recent measurements."""
    max_iso_timestamp = max_iso_timestamp or iso_timestamp()
    min_iso_timestamp = (datetime.fromisoformat(max_iso_timestamp) - timedelta(days=days)).isoformat()
    recent_measurements = database.measurements.find(
        filter={"end": {"$gt": min_iso_timestamp}, "start": {"$lt": max_iso_timestamp}},
        sort=[("start", pymongo.ASCENDING)], projection={"_id": False, "sources.entities": False})
    measurements_by_metric_uuid: Dict[MetricId, List] = {}
    for measurement in recent_measurements:
        measurements_by_metric_uuid.setdefault(measurement["metric_uuid"], []).append(measurement)
    return measurements_by_metric_uuid


def all_measurements(database: Database, metric_uuid: MetricId, max_iso_timestamp: str = ""):
    """Return all measurements, without the entities, except for the most recent one."""
    measurement_filter: Dict[str, Union[str, Dict[str, str]]] = {"metric_uuid": metric_uuid}
    if max_iso_timestamp:
        measurement_filter["start"] = {"$lt": max_iso_timestamp}
    latest_with_entities = database.measurements.find_one(
        measurement_filter, sort=[("start", pymongo.DESCENDING)], projection={"_id": False})
    if not latest_with_entities:
        return []
    all_measurements_without_entities = database.measurements.find(
        measurement_filter, projection={"_id": False, "sources.entities": False})
    return list(all_measurements_without_entities)[:-1] + [latest_with_entities]


def count_measurements(database: Database) -> int:
    """Return the number of measurements."""
    return int(database.measurements.count_documents(filter={}))


def update_measurement_end(database: Database, measurement_id: MeasurementId):
    """Set the end date and time of the measurement to the current date and time."""
    return database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})


def insert_new_measurement(database: Database, data_model, metric: Dict, measurement: Dict) -> Dict:
    """Insert a new measurement."""
    if "_id" in measurement:
        del measurement["_id"]
    metric_type = data_model["metrics"][metric["type"]]
    direction = metric.get("direction") or metric_type["direction"]
    for scale in metric_type["scales"]:
        value = calculate_measurement_value(data_model, metric, measurement["sources"], scale)
        status = determine_measurement_status(metric, direction, value)
        measurement[scale] = dict(value=value, status=status, direction=direction)
        for target in ("target", "near_target", "debt_target"):
            measurement[scale][target] = determine_target(
                metric, measurement, metric_type, scale, cast(TargetType, target))
    measurement["start"] = measurement["end"] = iso_timestamp()
    database.measurements.insert_one(measurement)
    del measurement["_id"]
    return measurement


def calculate_measurement_value(data_model, metric: Dict, sources, scale: Scale) -> Optional[str]:
    """Calculate the measurement value from the source measurements."""

    def percentage(numerator: int, denominator: int, direction: Direction) -> int:
        """Return the rounded percentage: numerator / denominator * 100%."""
        if denominator == 0:
            return 0 if direction == "<" else 100
        return int((100 * Decimal(numerator) / Decimal(denominator)).to_integral_value(ROUND_HALF_UP))

    def value_of_entities_to_ignore(source) -> int:
        """Return the value of ignored entities, i.e. entities marked as fixed, false positive or won't fix.

        If the entities have a measured attribute, return the sum of the measured attributes of the ignored
        entities, otherwise return the number of ignored attributes. For example, if the metric is the amount of ready
        user story points, the source entities are user stories and the measured attribute is the amount of story
        points of each user story.
        """
        entities = source.get("entity_user_data", {}).items()
        ignored_entities = [
            entity[0] for entity in entities if entity[1].get("status") in ("fixed", "false_positive", "wont_fix")]
        source_type = metric["sources"][source["source_uuid"]]["type"]
        if attribute := get_measured_attribute(data_model, metric["type"], source_type):
            entity = data_model["sources"][source_type]["entities"].get(metric["type"], {})
            attribute_type = get_attribute_type(entity, attribute)
            convert = dict(float=float, integer=int, minutes=int)[attribute_type]
            value = sum(
                convert(entity[attribute]) for entity in source["entities"] if entity["key"] in ignored_entities)
        else:
            value = len(ignored_entities)
        return int(value)

    if not sources or any(source["parse_error"] or source["connection_error"] for source in sources):
        return None
    values = [int(source["value"]) - value_of_entities_to_ignore(source) for source in sources]
    addition = metric["addition"]
    add = dict(max=max, min=min, sum=sum)[addition]
    if scale == "percentage":
        metric_type = data_model["metrics"][metric["type"]]
        direction = metric.get("direction") or metric_type["direction"]
        totals = [int(source["total"]) for source in sources]
        if addition == "sum":
            values, totals = [sum(values)], [sum(totals)]
        values = [percentage(value, total, direction) for value, total in zip(values, totals)]
    return str(add(values))  # type: ignore


def determine_measurement_status(metric, direction: Direction, measurement_value: Optional[str]) -> Optional[Status]:
    """Determine the measurement status."""
    debt_end_date = metric.get("debt_end_date") or date.max.isoformat()
    if measurement_value is None:
        # Allow for accepted debt even if there is no measurement yet so that the fact that a metric does not have a
        # source can be accepted as technical debt
        return "debt_target_met" if metric["accept_debt"] and date.today().isoformat() <= debt_end_date else None
    value = float(measurement_value)
    target = float(metric.get("target") or 0)
    near_target = float(metric.get("near_target") or 0)
    debt_target = float(metric.get("debt_target") or 0)
    better_or_equal = {">": float.__ge__, "<": float.__le__}[direction]
    if better_or_equal(value, target):
        status: Status = "target_met"
    elif metric["accept_debt"] and date.today().isoformat() <= debt_end_date and better_or_equal(value, debt_target):
        status = "debt_target_met"
    elif better_or_equal(target, near_target) and better_or_equal(value, near_target):
        status = "near_target_met"
    else:
        status = "target_not_met"
    return status


def determine_target(metric, measurement: Dict, metric_type, scale: Scale, target: TargetType):
    """Determine the (near) target."""
    metric_scale = metric.get("scale", "count")  # The current scale chosen by the user
    target_value = metric.get(target, metric_type.get(target)) if scale == metric_scale else \
        measurement.get(scale, {}).get(target)
    if target == "debt_target":
        debt_target_expired = (metric.get("debt_end_date") or date.max.isoformat()) < date.today().isoformat()
        debt_target_off = metric.get("accept_debt") is False
        if debt_target_expired or debt_target_off:
            target_value = None
    return target_value


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog for the measurements belonging the items with the specific uuids."""
    return database.measurements.find(
        filter={"delta.uuids": {"$in": list(uuids.values())}}, sort=[("start", pymongo.DESCENDING)],
        limit=nr_changes, projection=["delta", "start"])
