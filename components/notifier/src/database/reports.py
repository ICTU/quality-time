"""Reports collection."""

from typing import TYPE_CHECKING

from pymongo.database import Database

from shared.database.reports import get_reports
from shared.model.measurement import Measurement
from shared.model.report import Report, get_metrics_from_reports

from .measurements import get_recent_measurements

if TYPE_CHECKING:
    from shared.model.metric import Metric
    from shared.utils.type import MetricId


def get_reports_and_measurements(database: Database) -> tuple[list[Report], list[Measurement]]:
    """Get the reports and measurements from the database."""
    reports: list[Report] = get_reports(database)
    metrics: dict[MetricId, Metric] = get_metrics_from_reports(reports)
    return reports, get_recent_measurements(database, list(metrics.values()))
