"""Database initialization."""

import logging
import os

import pymongo  # pylint: disable=wrong-import-order
from pymongo.database import Database

from .datamodel import import_datamodel
from .report import import_example_reports, initialize_reports_overview
from .secrets import initialize_secrets


# For some reason the init_database() function gets reported as partially uncovered by the feature tests. Ignore.


def init_database() -> Database:  # pragma: no cover-behave
    """Initialize the database connection and contents."""
    database_url = os.environ.get("DATABASE_URL", "mongodb://root:root@localhost:27017")
    client = pymongo.MongoClient(database_url)
    set_feature_compatibility_version(client.admin)
    database = client.quality_time_db
    logging.info("Connected to database: %s", database)
    nr_reports = database.reports.count_documents({})
    nr_measurements = database.measurements.count_documents({})
    logging.info("Database has %d report documents and %d measurement documents", nr_reports, nr_measurements)
    create_indexes(database)
    import_datamodel(database)
    initialize_secrets(database)
    initialize_reports_overview(database)
    if os.environ.get("LOAD_EXAMPLE_REPORTS", "True").lower() == "true":
        import_example_reports(database)
    return database


def set_feature_compatibility_version(admin_database: Database) -> None:
    """Set the feature compatibility version to the current MongoDB version to prepare for upgrade to the next version.

    See https://docs.mongodb.com/manual/release-notes/4.4-upgrade-standalone/
    """
    admin_database.command("setFeatureCompatibilityVersion", "4.2")


def create_indexes(database: Database) -> None:
    """Create any indexes."""
    database.datamodels.create_index("timestamp")
    database.reports.create_index("timestamp")
    start_index = pymongo.IndexModel([("start", pymongo.ASCENDING)])
    latest_measurement_index = pymongo.IndexModel([("metric_uuid", pymongo.ASCENDING), ("start", pymongo.DESCENDING)])
    latest_successful_measurement_index = pymongo.IndexModel(
        [("metric_uuid", pymongo.ASCENDING), ("has_error", pymongo.ASCENDING), ("start", pymongo.DESCENDING)]
    )
    database.measurements.create_indexes([start_index, latest_measurement_index, latest_successful_measurement_index])
