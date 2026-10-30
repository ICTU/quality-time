"""Reports collection."""

from typing import TYPE_CHECKING, cast

from shared.database.reports import get_reports
from shared.model.report import get_metrics_from_reports

from models.report import Report

from .measurements import get_recent_measurements

if TYPE_CHECKING:
    from pymongo.database import Database

    from shared.model.measurement import Measurement
    from shared.model.metric import Metric
    from shared.utils.type import MetricId


def get_reports_and_measurements(database: Database) -> tuple[list[Report], list[Measurement]]:
    """Get the reports and measurements from the database."""
    reports = get_reports(database, Report)
    metrics: dict[MetricId, Metric] = get_metrics_from_reports(reports)
    return cast(list[Report], reports), get_recent_measurements(database, list(metrics.values()))
