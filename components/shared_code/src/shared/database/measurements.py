"""Measurements collection."""

import pymongo
from pymongo.database import Database

from shared.model.measurement import Measurement
from shared.model.metric import Metric


def latest_measurement(
    database: Database, metric: Metric, *, skip_measurements_with_error: bool = False
) -> Measurement | None:
    """Return the latest measurement."""
    measurement_filter: dict[str, bool | str] = {"metric_uuid": metric.uuid}
    sort_options = [("start", pymongo.DESCENDING)]
    if skip_measurements_with_error:
        measurement_filter["has_error"] = False
    latest = database.measurements.find_one(filter=measurement_filter, sort=sort_options)
    return None if latest is None else Measurement(metric, latest)


def insert_new_measurement(database: Database, measurement: Measurement) -> Measurement:
    """Insert a new measurement."""
    if latest := latest_measurement(database, measurement.metric):  # pragma: no feature-test-cover
        # No need to keep hashes around. This update is ignored if the latest measurement has no hash.
        database.measurements.update_one({"_id": latest["_id"]}, {"$unset": {"source_parameter_hash": ""}})
    measurement.update_measurement()
    if "_id" in measurement:  # pragma: no feature-test-cover
        del measurement["_id"]  # Remove the Mongo ID if present so this measurement can be re-inserted in the database.
    database.measurements.insert_one(measurement)
    del measurement["_id"]
    return measurement
