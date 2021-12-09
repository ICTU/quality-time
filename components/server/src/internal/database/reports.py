"""Reports collection."""

import pymongo
from pymongo.database import Database

from internal.model.report import Report
from internal.model.metric import Metric
from internal.server_utilities.type import MetricId
from .filters import DOES_NOT_EXIST
from .datamodels import latest_datamodel


# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


def latest_reports(database: Database, data_model: dict) -> list[Report]:
    """Return the latest, undeleted, reports in the reports collection."""
    report_dicts = database.reports.find({"last": True, "deleted": DOES_NOT_EXIST})
    return [Report(data_model, report_dict) for report_dict in report_dicts]


def latest_metric(database: Database, metric_uuid: MetricId) -> Metric | None:
    """Return the latest metric with the specified metric uuid."""
    data_model = latest_datamodel(database)
    for report in latest_reports(database, data_model):
        if metric_uuid in report.metric_uuids:
            return report.metrics_dict[metric_uuid]
    return None
