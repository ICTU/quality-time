"""Measurements collection."""

from typing import NewType

from pymongo import DESCENDING
from pymongo.database import Database

from shared.database.measurements import insert_new_measurement, latest_measurement
from shared.model.measurement import Measurement
from shared.utils.functions import iso_timestamp

from database.reports import latest_metric

MeasurementId = NewType("MeasurementId", str)


def create_measurement(database: Database, measurement_data: dict) -> None:
    """Put the measurement in the database."""
    metric_uuid = measurement_data["metric_uuid"]
    report_uuid = measurement_data["report_uuid"]
    if (metric := latest_metric(database, report_uuid, metric_uuid)) is None:
        return  # Metric does not exist, must've been deleted while being measured
    latest = latest_measurement(database, metric)
    measurement = Measurement(metric, measurement_data, previous_measurement=latest)
    if not measurement.sources_exist():
        return  # Measurement has sources that the metric does not have, must've been deleted while being measured
    if latest:
        if latest_successful := latest_measurement(database, metric, skip_measurements_with_error=True):
            measurement.copy_entity_first_seen_timestamps(latest_successful)
        measurement.copy_entity_user_data(latest if latest_successful is None else latest_successful)
        measurement.update_measurement()  # Update the scales so we can compare the two measurements
        if measurement.equals(latest) and no_measurement_requested_after(latest):
            # If the new measurement is equal to the latest one and no measurement update was requested, merge the
            # two measurements together. Don't merge the measurements together when a measurement was requested,
            # even if the new measurement value did not change, so that the frontend gets a new measurement count
            # via the number of measurements server-sent events endpoint and knows the requested measurement was done.
            update_measurement_end(database, latest["_id"])
            return
    elif original_metric_uuid := metric.get("copied_from"):
        # This is the first measurement for a copied metric, copy the entity user data from the original metric:
        query = {"filter": {"metric_uuid": original_metric_uuid}, "sort": [("start", DESCENDING)]}
        if (original_measurement := database.measurements.find_one(**query)) and (
            original_metric := latest_metric(database, original_measurement["report_uuid"], original_metric_uuid)
        ):
            measurement.copy_entity_user_data(Measurement(original_metric, original_measurement))
    insert_new_measurement(database, measurement)


def update_measurement_end(database: Database, measurement_id: MeasurementId) -> None:  # pragma: no feature-test-cover
    """Set the end date and time of the measurement to the current date and time."""
    database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})


def no_measurement_requested_after(measurement: Measurement) -> bool:
    """Return whether a measurement was requested later than the end of this measurement."""
    if measurement_request_timestamp := measurement.metric.get("measurement_requested"):
        return bool(measurement_request_timestamp < measurement["end"])
    return True
