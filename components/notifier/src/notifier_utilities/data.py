"""Database interaction functions for the notifier."""

import os

import pymongo
from shared.initialization.database import create_indexes
from shared.initialization.datamodel import import_datamodel
from shared.initialization.report import initialize_reports_overview
from shared.initialization.secrets import initialize_secrets
from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.model.report import Report
from shared_data_model import DATA_MODEL


def client(url: str | None = "mongodb://root:root@localhost:27017") -> pymongo.MongoClient:
    """Return a pymongo client."""
    database_url = os.environ.get("DATABASE_URL", url)
    return pymongo.MongoClient(database_url)


def database(url: str | None = "mongodb://root:root@localhost:27017") -> pymongo.database.Database:
    """Return a pymongo database."""
    db_client = client(url)
    create_indexes(db_client["quality_time_db"])
    import_datamodel(db_client["quality_time_db"])
    initialize_secrets(db_client["quality_time_db"])
    initialize_reports_overview(db_client["quality_time_db"])
    return db_client["quality_time_db"]


def get_reports() -> list[Report]:
    """Return a list of reports."""
    qt_database = database()
    query = {"last": True, "deleted": {"$exists": False}}
    return [Report(DATA_MODEL.dict(), report_dict) for report_dict in qt_database["reports"].find(filter=query)]


def recent_measurements(*metrics: Metric, limit_per_metric: int = 2) -> list[Measurement]:
    """Return recent measurements for the specified metrics, without entities and issue status."""
    qt_database = database()
    projection = {
        "_id": False,
        "sources.entities": False,
        "sources.entity_user_data": False,
        "issue_status": False,
    }
    measurements: list = []

    for metric in metrics:
        measurements.extend(
            list(
                qt_database["measurements"].find(
                    {"metric_uuid": metric.uuid},
                    limit=limit_per_metric,
                    sort=[("start", pymongo.DESCENDING)],
                    projection=projection,
                ),
            ),
        )

    return measurements


def get_metrics_from_reports(reports: list[Report]) -> list[Metric]:
    """Return the metrics from the reports."""
    metrics: list[Metric] = []

    for report in reports:
        metrics.extend(report.metrics)
    return metrics


def get_reports_and_measurements() -> tuple[list[Report], list[Measurement]]:
    """Get the reports and measurements from the database."""
    reports: list[Report] = get_reports()
    metrics: list[Metric] = get_metrics_from_reports(reports)
    return reports, recent_measurements(*metrics)
