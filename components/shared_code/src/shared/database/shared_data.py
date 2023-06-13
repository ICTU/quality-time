"""Module with collection of methods that touch multiple data types."""

from pymongo.database import Database

from shared.database.filters import DOES_NOT_EXIST
from shared.database.measurements import (
    get_recent_measurements,
    insert_new_measurement,
    latest_measurement,
    latest_successful_measurement,
    update_measurement_end,
)
from shared.database.metrics import get_metrics_from_reports
from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.model.report import Report
from shared.utils.type import MetricId, ReportId
from shared_data_model import DATA_MODEL


def get_reports_and_measurements(database: Database) -> tuple[list[Report], list[Measurement]]:
    """Get the reports and measurements from the database."""
    reports: list[Report] = get_reports(database)
    metrics: dict[MetricId, Metric] = get_metrics_from_reports(reports)
    return reports, get_recent_measurements(database, list(metrics.values()))


def latest_metric(database: Database, report_uuid: ReportId, metric_uuid: MetricId) -> Metric | None:
    """Return the latest metric with the specified metric uuid."""
    report = _latest_report(database, report_uuid)
    return report.metrics_dict.get(metric_uuid) if report else None


def _latest_report(database: Database, report_uuid: ReportId) -> Report | None:
    """Get latest report with this uuid."""
    report_dict = database.reports.find_one({"report_uuid": report_uuid, "last": True, "deleted": DOES_NOT_EXIST})
    return Report(DATA_MODEL.dict(), report_dict) if report_dict else None


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
        latest_successful = latest_successful_measurement(database, metric)
        measurement.copy_entity_user_data(latest if latest_successful is None else latest_successful)
        measurement.update_measurement()  # Update the scales so we can compare the two measurements
        if measurement.equals(latest):
            # If the new measurement is equal to the previous one, merge them together
            update_measurement_end(database, latest["_id"])
            return
    insert_new_measurement(database, measurement)


def latest_reports(database: Database) -> list[Report]:
    """Return the latest, undeleted, reports in the reports collection."""
    report_dicts = database.reports.find({"last": True, "deleted": DOES_NOT_EXIST})
    return [Report(DATA_MODEL.dict(), report_dict) for report_dict in report_dicts]


def get_reports(database: Database) -> list[Report]:
    """Return a list of reports."""
    query = {"last": True, "deleted": {"$exists": False}}
    return [Report(DATA_MODEL.dict(), report_dict) for report_dict in database["reports"].find(filter=query)]
