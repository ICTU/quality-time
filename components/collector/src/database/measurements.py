"""Measurements collection."""

from typing import NewType

from pymongo.database import Database

from shared.database.measurements import insert_new_measurement, latest_measurement, latest_successful_measurement
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
        if latest_successful := latest_successful_measurement(database, metric):
            measurement.copy_entity_first_seen_timestamps(latest_successful)
        measurement.copy_entity_user_data(latest if latest_successful is None else latest_successful)
        measurement.update_measurement()  # Update the scales so we can compare the two measurements
        if measurement.equals(latest):
            # If the new measurement is equal to the previous one, merge them together
            update_measurement_end(database, latest["_id"])
            return
    insert_new_measurement(database, measurement)


def update_measurement_end(database: Database, measurement_id: MeasurementId) -> None:  # pragma: no feature-test-cover
    """Set the end date and time of the measurement to the current date and time."""
    database.measurements.update_one(filter={"_id": measurement_id}, update={"$set": {"end": iso_timestamp()}})
