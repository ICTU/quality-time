"""Database initialization."""

import logging
import os

import bottle
import pymongo  # pylint: disable=wrong-import-order

from ..route_injection_plugin import InjectionPlugin
from .datamodel import import_datamodel
from .report import import_example_reports, initialize_reports_overview


def init_database() -> None:
    """Initialize the database connection and contents."""
    database_url = os.environ.get("DATABASE_URL", "mongodb://root:root@localhost:27017")
    database = pymongo.MongoClient(database_url).quality_time_db
    database_injection_plugin = InjectionPlugin(value=database, keyword="database")
    bottle.install(database_injection_plugin)
    logging.info("Connected to database: %s", database)
    nr_reports = database.reports.count_documents({})
    nr_measurements = database.measurements.count_documents({})
    logging.info("Database has %d report documents and %d measurement documents", nr_reports, nr_measurements)
    import_datamodel(database)
    initialize_reports_overview(database)
    import_example_reports(database)
