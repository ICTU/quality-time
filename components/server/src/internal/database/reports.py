"""Reports collection."""

from pymongo.database import Database

from server_utilities.type import MetricId
from shared.model.metric import Metric
from database.reports import latest_reports

from .datamodels import latest_datamodel


def latest_metric(database: Database, metric_uuid: MetricId) -> Metric | None:
    """Return the latest metric with the specified metric uuid."""
    data_model = latest_datamodel(database)
    for report in latest_reports(database, data_model):
        if metric_uuid in report.metric_uuids:
            return report.metrics_dict[metric_uuid]
    return None
