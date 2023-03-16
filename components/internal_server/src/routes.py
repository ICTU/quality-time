import logging

from shared.database.measurements import insert_new_measurement, latest_measurement
from shared.model.measurement import Measurement

from database import latest_successful_measurement, update_measurement_end, recent_measurements
from models import BaseMetrics, DictOfMeasurements

from fastapi import APIRouter, HTTPException
from shared.initialization.database import get_database
#                                           )
from models import BaseMeasurement, BaseReport
from reports import latest_metric, latest_reports

DATABASE = get_database()

health = APIRouter(
    prefix="/api",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)

measurements = APIRouter(
    prefix="/api",
    tags=["measurements"],
    responses={404: {"description": "Not found"}},
)

reports = APIRouter(
    prefix="/api",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

metrics = APIRouter(
    prefix="/api",
    tags=["metrics"],
    responses={404: {"description": "Not found"}},
)


@health.get("/health")
def get_health():
    return {"status": "ok"}


@reports.get("/reports", response_model=list[BaseReport])
def get_reports() -> list[BaseReport]:
    reports = latest_reports(DATABASE)
    logging.error(reports)
    return reports


@measurements.post("/measurements", response_model=BaseMeasurement)
def post_measurement(base_measurement: BaseMeasurement) -> dict:
    """Put the measurement in the database."""
    if (metric := latest_metric(DATABASE, base_measurement.report_uuid, base_measurement.metric_uuid)) is None:
        raise HTTPException(
            status_code=422, detail="Metric does not exist, must've been deleted while being measured")
    latest = latest_measurement(DATABASE, metric)
    measurement = Measurement(metric, base_measurement,
                              previous_measurement=latest)
    if not measurement.sources_exist():
        raise HTTPException(
            status_code=422, detail="Metric does not exist, must've been deleted while being measured")
    if latest:
        latest_successful = latest_successful_measurement(
            DATABASE, metric)
        measurement.copy_entity_user_data(
            latest if latest_successful is None else latest_successful)
        # Update the scales so we can compare the two measurements
        measurement.update_measurement()
        if measurement.equals(latest):
            # If the new measurement is equal to the previous one, merge them together
            return BaseMeasurement(update_measurement_end(DATABASE, latest["_id"]))
    insert_new_measurement(DATABASE, measurement)

    return dict(base_measurement)


@measurements.get("/measurements", response_model=DictOfMeasurements)
def get_measurements():
    metrics: list[Metric] = []
    for report in latest_reports(DATABASE):
        metrics.extend(report.metrics)

    # TODO: seems odd to use dict to display list of measurements. Make this a list of measurements
    return dict(measurements=recent_measurements(DATABASE, *metrics))


@metrics.get("/metrics", response_model=BaseMetrics)
def get_metrics():
    """Get all metrics."""
    metrics: dict[str, Any] = {}
    # DeepSource somehow confuses latest_reports() with another latest_reports() that needs two arguments, suppress.
    for report in latest_reports(DATABASE):  # skipcq: PYL-E1120
        logging.error(report)
        issue_tracker = report.get("issue_tracker", {})
        has_issue_tracker = bool(issue_tracker.get(
            "type") and issue_tracker.get("parameters", {}).get("url"))
        for metric in report.metrics:
            metric["report_uuid"] = report["report_uuid"]
            if has_issue_tracker and metric.get("issue_ids"):
                metric["issue_tracker"] = issue_tracker
            metrics[metric.uuid] = metric.summarize(
                [], report_uuid=report.uuid)
    return metrics
