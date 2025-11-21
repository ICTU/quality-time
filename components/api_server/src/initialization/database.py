"""Database initialization."""

import os
from typing import TYPE_CHECKING

import pymongo

from utils.log import get_logger

from .app_secrets import initialize_secrets
from .datamodel import import_datamodel
from .report import import_example_reports, initialize_reports_overview

if TYPE_CHECKING:
    from pymongo.database import Database


def init_database(database: Database) -> None:  # pragma: no feature-test-cover
    """Initialize the database contents."""
    logger = get_logger()
    logger.info("Connected to database: %s", database)
    nr_reports = database.reports.count_documents({})
    nr_measurements = database.measurements.count_documents({})
    logger.info("Database has %d report documents and %d measurement documents", nr_reports, nr_measurements)
    create_indexes(database)
    import_datamodel(database)
    initialize_secrets(database)
    initialize_reports_overview(database)
    if os.environ.get("LOAD_EXAMPLE_REPORTS", "True").lower() == "true":
        import_example_reports(database)


def set_feature_compatibility_version(admin_database: Database) -> None:
    """Set the feature compatibility version to the current MongoDB version to prepare for upgrade to the next version.

    See https://docs.mongodb.com/manual/reference/command/setFeatureCompatibilityVersion/
    """
    admin_database.command("setFeatureCompatibilityVersion", "8.0", confirm=True)


def create_indexes(database: Database) -> None:
    """Create any indexes."""
    database.datamodels.create_index("timestamp")
    database.reports.create_index([("timestamp", pymongo.ASCENDING), ("report_uuid", pymongo.ASCENDING)])
    database.users.create_index("username", unique=True)
    period_index = pymongo.IndexModel([("start", pymongo.ASCENDING), ("end", pymongo.DESCENDING)])
    latest_measurement_index = pymongo.IndexModel([("metric_uuid", pymongo.ASCENDING), ("start", pymongo.DESCENDING)])
    latest_successful_measurement_index = pymongo.IndexModel(
        [("metric_uuid", pymongo.ASCENDING), ("has_error", pymongo.ASCENDING), ("start", pymongo.DESCENDING)],
    )
    database.measurements.create_indexes([period_index, latest_measurement_index, latest_successful_measurement_index])
