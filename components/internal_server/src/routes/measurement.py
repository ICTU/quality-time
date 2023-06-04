"""Measurement routes."""

import bottle
from pymongo.database import Database

from shared.database.measurements import insert_new_measurement, latest_measurement
from shared.model.measurement import Measurement
from shared.model.metric import Metric
from database.reports import latest_metric, latest_reports

from database.measurements import latest_successful_measurement, recent_measurements, update_measurement_end


@bottle.post("/api/measurements")
def post_measurement(database: Database) -> None:
    """Put the measurement in the database."""
    measurement_data = dict(bottle.request.json)
    metric_uuid = measurement_data["metric_uuid"]
    report_uuid = measurement_data["report_uuid"]
    if (metric := latest_metric(database, report_uuid, metric_uuid)) is None:
        return  # Metric does not exist, must've been deleted while being measured
    latest = latest_measurement(database, metric)
    measurement = Measurement(metric, measurement_data, previous_measurement=latest)
    if not measurement.sources_exist():
        return  # Measurement has sources that the metric does not have, must've been deleted while being measured
    if latest:
        latest_successful = latest_successful_measurement(database, metric)
        measurement.copy_entity_user_data(latest if latest_successful is None else latest_successful)
        measurement.update_measurement()  # Update the scales so we can compare the two measurements
        if measurement.equals(latest):
            # If the new measurement is equal to the previous one, merge them together
            update_measurement_end(database, latest["_id"])
            return
    insert_new_measurement(database, measurement)


@bottle.get("/api/measurements")
def get_measurements(database: Database):
    """Return the two most recent measurements (without details) for all metrics in all reports."""
    metrics: list[Metric] = []
    for report in latest_reports(database):
        metrics.extend(report.metrics)
    return dict(measurements=recent_measurements(database, *metrics))
