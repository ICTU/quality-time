"""Database initialization."""

import logging
import os

import pymongo  # pylint: disable=wrong-import-order
from pymongo.database import Database

from .datamodel import import_datamodel
from .report import import_example_reports, initialize_reports_overview


# For some reason the init_database() function gets reported as partially uncovered by the feature tests. Ignore.

def init_database() -> Database:  # pragma: no cover-behave
    """Initialize the database connection and contents."""
    database_url = os.environ.get("DATABASE_URL", "mongodb://root:root@localhost:27017")
    database = pymongo.MongoClient(database_url).quality_time_db
    logging.info("Connected to database: %s", database)
    nr_reports = database.reports.count_documents({})
    nr_measurements = database.measurements.count_documents({})
    logging.info("Database has %d report documents and %d measurement documents", nr_reports, nr_measurements)
    create_indexes(database)
    import_datamodel(database)
    initialize_reports_overview(database)
    if os.environ.get("LOAD_EXAMPLE_REPORTS", "True").lower() == "true":
        import_example_reports(database)
    return database


def create_indexes(database: Database) -> None:
    """Create any indexes."""
    database.reports.create_index("timestamp")
    database.measurements.create_index("start")
