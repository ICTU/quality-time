"""Reports collection."""

from pymongo.database import Database

from shared.database.datamodels import latest_datamodel
from shared.database.filters import DOES_NOT_EXIST
from shared.model.metric import Metric
from shared.model.report import Report
from shared.utils.type import MetricId, ReportId


def latest_reports(database: Database, data_model: dict) -> list[Report]:
    """Return the latest, undeleted, reports in the reports collection."""
    report_dicts = database.reports.find({"last": True, "deleted": DOES_NOT_EXIST})
    return [Report(data_model, report_dict) for report_dict in report_dicts]


def latest_report(database: Database, data_model: dict, report_uuid: ReportId) -> Report | None:
    """Get latest report with this uuid."""
    report_dict = database.reports.find_one({"report_uuid": report_uuid, "last": True, "deleted": DOES_NOT_EXIST})
    return Report(data_model, report_dict) if report_dict else None


def latest_metric(database: Database, report_uuid: ReportId, metric_uuid: MetricId) -> Metric | None:
    """Return the latest metric with the specified metric uuid."""
    data_model = latest_datamodel(database)
    report = latest_report(database, data_model, report_uuid)
    return report.metrics_dict.get(metric_uuid) if report else None
