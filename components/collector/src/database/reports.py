"""Reports collection."""

from typing import TYPE_CHECKING

from shared.database.filters import DOES_NOT_EXIST
from shared.model.report import Report
from shared_data_model import DATA_MODEL

if TYPE_CHECKING:
    from pymongo.database import Database

    from shared.model.metric import Metric
    from shared.utils.type import MetricId, ReportId


def latest_metric(database: Database, report_uuid: ReportId, metric_uuid: MetricId) -> Metric | None:
    """Return the latest metric with the specified metric uuid."""
    report_dict = database.reports.find_one({"report_uuid": report_uuid, "last": True, "deleted": DOES_NOT_EXIST})
    return Report(DATA_MODEL.model_dump(), report_dict).metrics_dict.get(metric_uuid) if report_dict else None
